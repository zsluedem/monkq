#
# MIT License
#
# Copyright (c) 2018 WillQ
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import csv
import datetime
import io
import os
import shutil
import zlib
from typing import IO, Generator, Iterator, List, Set, Type

import pandas
import requests
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from logbook import Logger
from MonkTrader.config.global_settings import (
    HDF_FILE_COMPRESS_LEVEL, HDF_FILE_COMPRESS_LIB,
)
from MonkTrader.data import (
    DataDownloader, DownloadProcess, Point, ProcessPoints,
)
from MonkTrader.exception import DataDownloadError
from MonkTrader.exchange.bitmex.const import (
    INSTRUMENT_FILENAME, QUOTE_FILE_NAME, QUOTE_LINK, START_DATE, SYMBOL_LINK,
    TARFILETYPE, TRADE_FILE_NAME, TRADE_LINK,
)
from MonkTrader.utils import CsvFileDefaultDict, CsvZipDefaultDict, assure_dir
from MonkTrader.utils.i18n import _

from ..log import logger_group
from .utils import classify_df, read_quote_tar, read_trade_tar

logger = Logger('exchange.bitmex.data')
logger_group.add_logger(logger)


class DatePoint(Point):
    def __init__(self, date: datetime.datetime, url: str, dst_dir: str):
        self.date = date
        self.url = url
        self.dst_dir = dst_dir

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DatePoint):
            raise NotImplementedError()
        return self.date == other.date

    @property
    def value(self) -> datetime.datetime:
        return self.date


class BitMexProcessPoints(ProcessPoints):
    def __init__(self, start: datetime.datetime, end: datetime.datetime, link: str, dst_dir: str):
        self.start = start + relativedelta(hour=0, minute=0, second=0, microsecond=0)
        self.end = end + relativedelta(hour=0, minute=0, second=0, microsecond=0)
        self.current = start

        self.rruls_date = rrule(freq=DAILY, dtstart=self.start, until=self.end)

        self.link = link
        self.dst_dir = dst_dir

    def __iter__(self) -> Iterator[DatePoint]:
        for date in rrule(freq=DAILY, dtstart=self.start, until=self.end):
            yield DatePoint(date, self.link.format(date.strftime("%Y%m%d")), self.dst_dir)


class BitMexDownloader(DataDownloader):
    def __init__(self, kind: str, mode: str, dst_dir: str):
        logger.info(_('Start downloading the data'))
        self.mode = mode
        self.kind = kind
        self.dst_dir = dst_dir
        self.init_kind(mode, kind)
        self.init_mode(dst_dir)
        self.Streamer: Type[DownloadProcess]

    def init_kind(self, mode: str, kind: str) -> None:
        if kind == 'quote':
            self.link = QUOTE_LINK
            if mode == 'csv':
                self.Streamer = QuoteZipFileStream
            elif mode == 'tar':
                self.Streamer = TarStreamRequest
            elif mode == 'hdf':
                self.Streamer = HDFQuoteStream
            else:
                raise ValueError
        elif kind == 'trade':
            self.link = TRADE_LINK
            if mode == 'csv':
                self.Streamer = TradeZipFileStream
            elif mode == 'tar':
                self.Streamer = TarStreamRequest
            elif mode == 'hdf':
                self.Streamer = HDFTradeStream
            else:
                raise ValueError
        elif kind == 'instruments':
            self.link = SYMBOL_LINK
            self.Streamer = SymbolsStreamRequest
        else:
            raise ValueError()

    def init_mode(self, dst_dir: str) -> None:
        self.end = datetime.datetime.utcnow() + relativedelta(days=-1, hour=0, minute=0, second=0, microsecond=0)
        self.start = self.Streamer.get_start(dst_dir)

    def process_point(self) -> BitMexProcessPoints:
        return BitMexProcessPoints(self.start, self.end, self.link, self.dst_dir)

    def download_one_point(self, point: DatePoint) -> None:
        logger.info(_('Downloading {} data on {}').format(self.kind, point.value.isoformat()))
        qstream = self.Streamer(point=point)
        qstream.process()
        logger.info(_('Finished downloading {} data on {}').format(self.kind, point.value.isoformat()))


class StreamRequest():
    def _stream_requests(self, url: str) -> Generator[bytes, None, None]:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=io.DEFAULT_BUFFER_SIZE):
            yield chunk


class FileObjRequest():
    def _stream_requests(self, url: str) -> IO:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.raw


class _HDFStream(FileObjRequest, DownloadProcess):
    kind: str

    def __init__(self, point: DatePoint):
        super(_HDFStream, self).__init__(point=point)
        self.url = point.url
        assure_dir(point.dst_dir)
        self.dst_dir = point.dst_dir

        if self.kind == 'trade':
            self.dst_file = os.path.join(self.dst_dir, TRADE_FILE_NAME)
        elif self.kind == 'quote':
            self.dst_file = os.path.join(self.dst_dir, QUOTE_FILE_NAME)
        self.process_point = point

        self.processed_key: Set = set()

    def process(self) -> None:
        try:
            if self.kind == 'trade':
                dataframe = read_trade_tar(self._stream_requests(self.url), index='timestamp')
            elif self.kind == 'quote':
                dataframe = read_quote_tar(self._stream_requests(self.url), index='timestamp')
            cla_df = classify_df(dataframe, 'symbol')
            for key, df in cla_df.items():
                self.processed_key.add(key)
                df.to_hdf(self.dst_file, key, mode='a',
                          format='table', data_columns=True, index=False,
                          complib=HDF_FILE_COMPRESS_LIB, complevel=HDF_FILE_COMPRESS_LEVEL, append=True)
        except Exception as e:
            self.rollback()
            logger.exception(_("Exception #{}# happened when process {} {}").format(e, self.url, self.dst_file))
            raise DataDownloadError()

    def rollback(self) -> None:
        date = self.process_point.value
        with pandas.HDFStore(self.dst_file) as store:
            for key in self.processed_key:
                store.remove(key, "index>=datetime.datetime({},{},{})".format(date.year, date.month, date.day))

    @classmethod
    def get_start(cls, dst_dir: str) -> datetime.datetime:
        if cls.kind == 'quote':
            filename = QUOTE_FILE_NAME
        elif cls.kind == 'trade':
            filename = TRADE_FILE_NAME
        else:
            raise Exception("kind should be quote or trade")
        try:
            with pandas.HDFStore(os.path.join(dst_dir, filename), 'r') as store:
                keys = store.keys()
                max_date = START_DATE
                for key in keys:
                    index = store.select_column(key, 'index')
                    last = max(index)
                    max_date = max(max_date, last)
                last_date = datetime.datetime(max_date.year, max_date.month, max_date.day)
                return last_date + relativedelta(days=+1)

        except (KeyError, OSError):
            return START_DATE


class HDFTradeStream(_HDFStream):
    kind = 'trade'


class HDFQuoteStream(_HDFStream):
    kind = 'quote'


class RawStreamRequest(StreamRequest, DownloadProcess):
    """
    Stream a url request and save the raw contents to local.
    The child class has to be configured the `FILENAME`

    If anything exception happens in the process,
    the stream file would be deleted and raise `DataDownloadException`.

    :param url: the url used to stream, the url should be response
        content not just header.
    :param dst_dir: the content would save to the dst_dir directory
        with the `FILENAME`.
    """
    FILENAME: str

    def __init__(self, point: DatePoint):
        super(RawStreamRequest, self).__init__(point=point)
        self.url = point.url
        assure_dir(point.dst_dir)
        self.dst_dir = point.dst_dir

        self.dst_file = os.path.join(self.dst_dir, self.FILENAME)

    def process(self) -> None:
        try:
            with open(self.dst_file, 'wb') as f:
                for chunk in self._stream_requests(self.url):
                    f.write(chunk)
        except Exception as e:
            self.rollback()
            logger.exception(_("Exception #{}# happened when process {} {}").format(e, self.url, self.dst_file))
            raise DataDownloadError()

    def rollback(self) -> None:
        logger.info(_("Rollback!Remove the not complete file {}").format(self.dst_file))
        os.remove(self.dst_file)

    @classmethod
    def get_start(cls, dst_dir: str) -> datetime.datetime:
        dones = os.listdir(dst_dir)
        if dones:
            current = max(dones)
            return datetime.datetime.strptime(current, "%Y%m%d" + TARFILETYPE) + relativedelta(days=+1)
        else:
            return START_DATE


class TarStreamRequest(RawStreamRequest):
    def __init__(self, point: DatePoint):
        self.FILENAME = point.date.strftime("%Y%m%d") + '.csv.gz'
        super(TarStreamRequest, self).__init__(point=point)


class SymbolsStreamRequest(RawStreamRequest):
    FILENAME: str = INSTRUMENT_FILENAME

    @classmethod
    def get_start(cls, dst_dir: str) -> datetime.datetime:
        return datetime.datetime.utcnow() + relativedelta(days=-1, hour=0, minute=0, second=0, microsecond=0)


class _CsvStreamRequest(StreamRequest, DownloadProcess):
    """
    A base class to process the stream a url request
    which would return a zip csv file.
    If any Exceptions happened in the process ,
    the class would trigger `rollback` and raise `DataDownloadException` error.
    After all data are finished streaming, `cleanup` would trigger.

    The child class has to implement `setup`, `process_chunk`, `process_row`

    :param date: the date for the class to process
    :param url: use the url to stream the response to process
    :param cache_num: it worked with the param chunk_process ,
    if the chunk_process is True, the class would process the csv rows
        when the cached items reach to the cache_num
    :param chunk_process: If chunk_process is True ,
        the class would process with cached items.Otherwise,
        it would process row by row.
    """

    def __init__(self, point: DatePoint, cache_num: int = 100, chunk_process: bool = False,
                 csv_reader: Type[csv.DictReader] = csv.DictReader):
        super(_CsvStreamRequest, self).__init__(point=point)
        self.date = point.date
        self.url = point.url
        self.cache_num = cache_num
        self.chunk_process = chunk_process
        self.data = bytearray()
        self.cache: List = list()
        self.csv_reader = csv_reader
        self.dec = zlib.decompressobj(32 + zlib.MAX_WBITS)

    def setup(self) -> None:
        raise NotImplementedError

    def stream_decompress_requests(self) -> Generator[str, None, None]:
        for chunk in self._stream_requests(self.url):
            rv = self.dec.decompress(chunk)
            if rv:
                self.data.extend(rv)
                while 1:
                    pos = self.data.find(b'\n')
                    if pos == -1:
                        break
                    else:
                        line, self.data = self.data[:pos + 1], self.data[pos + 1:]
                        yield line.decode('utf8')

    def process(self) -> None:
        try:
            self.setup()
            for i, row in enumerate(self.csv_reader(self.stream_decompress_requests())):
                if self.chunk_process:
                    self.cache.append(self.process_row(row))
                    if i % self.cache_num == 0:
                        self.process_chunk()
                        self.cache = list()
                else:
                    self.process_row(row)
            if self.cache:
                self.process_chunk()
        except BaseException as e:
            self.rollback()
            logger.exception(_("Exception {} happened when process {} data").format(e, self.date))
            raise DataDownloadError()
        self.cleanup()

    def rollback(self) -> None:
        pass

    def cleanup(self) -> None:
        pass

    def process_chunk(self) -> None:
        raise NotImplementedError

    def process_row(self, row: dict) -> dict:
        return row


class _FileStream(_CsvStreamRequest):
    """
    The child class which inherit this class has to be configured
    the filednames which are used to generate the csv headers.
    It takes a url and a destination directory to init and
    the class would stream the url response to several single files
    which are classified by the symbol name.

    The directory structure would be like :

    dst_dir
    |
    +--date1
    |    |
    |    |---symbol_name.csv
    |    |---symbol_name.csv
    |
    +--date2
    |    |
    |    |---symbol_name.csv
    |    |---symbol_name.csv
    |
    .......


    """
    fieldnames: List = list()

    def __init__(self, point: DatePoint, writer_cls: Type = CsvFileDefaultDict):
        super(_FileStream, self).__init__(point=point, chunk_process=False)
        assert os.path.isdir(point.dst_dir)
        new_dir = os.path.join(point.dst_dir, self.date.strftime("%Y%m%d"))
        self.dst_dir = new_dir
        self.csv_file_writers = writer_cls(self.dst_dir, self.fieldnames)

    def setup(self) -> None:
        if not os.path.exists(self.dst_dir):
            os.mkdir(self.dst_dir)

    def process_row(self, row: dict) -> dict:
        writer = self.csv_file_writers[row['symbol']]
        writer.writerow(row)
        return row

    def rollback(self) -> None:
        logger.info(_("Rollback : Remove the not complete dir {}").format(self.dst_dir))
        self.csv_file_writers.close()
        shutil.rmtree(self.dst_dir)

    def cleanup(self) -> None:
        self.csv_file_writers.close()

    @classmethod
    def get_start(cls, dst_dir: str) -> datetime.datetime:
        dones = os.listdir(dst_dir)
        if dones:
            current = max(dones)
            return datetime.datetime.strptime(current, "%Y%m%d") + relativedelta(days=+1)
        else:
            return START_DATE


class _ZipFileStream(_FileStream):
    """
    Instead of saving raw csv file in the directory, this class save
    a compressed csv into local to save storage.
    """
    DEFAULT = 'DEFAULT'

    def __init__(self, point: DatePoint, writer_cls: Type = CsvZipDefaultDict):
        super(_ZipFileStream, self).__init__(point, writer_cls)

    def process_row(self, row: dict) -> dict:
        f = self.csv_file_writers[row['symbol']]
        row_tuple = [row.get(key, self.DEFAULT) for key in self.fieldnames]
        self.csv_file_writers.writerow(f, row_tuple)
        return row


class TradeZipFileStream(_ZipFileStream):
    fieldnames = ["timestamp", "symbol", "side", "size", "price", "tickDirection", "trdMatchID", "grossValue",
                  "homeNotional", "foreignNotional"]


class QuoteZipFileStream(_ZipFileStream):
    fieldnames = ["timestamp", "symbol", "bidSize", "bidPrice", "askPrice", "askSize"]
