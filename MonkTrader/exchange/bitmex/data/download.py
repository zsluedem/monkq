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
import pandas
from typing import Generator

import requests
from logbook import Logger
from dateutil.relativedelta import relativedelta
from MonkTrader.exception import DataDownloadError
from MonkTrader.exchange.bitmex.const import INSTRUMENT_FILENAME, TARFILETYPE
from MonkTrader.utils import CsvFileDefaultDict, CsvZipDefaultDict, assure_dir
from MonkTrader.utils.i18n import _

from ..log import logger_group
from .utils import read_trade_tar, classify_df, read_quote_tar

logger = Logger('exchange.bitmex.data')
logger_group.add_logger(logger)

START_DATE = datetime.datetime(2014, 11, 22)  # bitmex open date


def _hdf_file(name: str):
    return "{}.hdf".format(name)


class StreamRequest():
    def _stream_requests(self, url: str) -> Generator[bytes, None, None]:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=io.DEFAULT_BUFFER_SIZE):
            yield chunk


class FileObjRequest():
    def _stream_requests(self, url: str):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.raw


class _DownloadProcess():
    """
    Each download process should include two method -- "process" and "rollback".
    The "process" is to do the download main function.If there are any exceptions happened in
    "process"， "rollback" should be trigger and clean up the data in "process".

    classmethod "get_start" is used to get the start point from history.
    """

    def process(self):
        """
        process the data after the raw_process data
        :return:
        """
        raise NotImplementedError()

    def rollback(self):
        """
        If there is anything wrong happening in the process, the whole process would rollback
        :return:
        """
        raise NotImplementedError()

    @classmethod
    def get_start(cls, *args, **kwargs):
        raise NotImplementedError()


class _HDFStream(FileObjRequest, _DownloadProcess):
    kind = None

    def __init__(self, url: str, dst_dir: str, *args, **kwargs):
        self.url = url
        assure_dir(dst_dir)
        self.dst_dir = dst_dir

        self.dst_file = os.path.join(self.dst_dir, _hdf_file(self.kind))
        self.process_point = kwargs.get("point")

        self.processed_key = set()

    def process(self):
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
                          complib='blosc:blosclz', complevel=9, append=True)
        except Exception as e:
            self.rollback()
            logger.exception(_("Exception #{}# happened when process {} {}").format(e, self.url, self.dst_file))
            raise DataDownloadError()

    def rollback(self):
        date = self.process_point.value
        with pandas.HDFStore(self.dst_file) as store:
            for key in self.processed_key:
                store.remove(key, "index>=datetime.datetime({},{},{})".format(date.year, date.month, date.day))

    @classmethod
    def get_start(cls, dst_dir: str):
        try:
            with pandas.HDFStore(os.path.join(dst_dir, _hdf_file(cls.kind)), 'r') as store:
                keys = store.keys()
                max_date = None
                for key in keys:
                    index = store.select_column(key, 'index')
                    last = max(index)
                    if max_date is None:
                        max_date = last
                    else:
                        max_date = max(max_date, last)
                last_date = datetime.datetime(max_date.year, max_date.month, max_date.day)
                return last_date + relativedelta(days=+1)

        except (KeyError, OSError):
            return START_DATE


class HDFTradeStream(_HDFStream):
    kind = 'trade'


class HDFQuoteStream(_HDFStream):
    kind = 'quote'


class RawStreamRequest(StreamRequest, _DownloadProcess):
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
    FILENAME = None

    def __init__(self, url: str, dst_dir: str, *args, **kwargs):
        self.url = url
        assure_dir(dst_dir)
        self.dst_dir = dst_dir

        self.dst_file = os.path.join(self.dst_dir, self.FILENAME)

    def process(self):
        try:
            with open(self.dst_file, 'wb') as f:
                for chunk in self._stream_requests(self.url):
                    f.write(chunk)
        except Exception as e:
            self.rollback()
            logger.exception(_("Exception #{}# happened when process {} {}").format(e, self.url, self.dst_file))
            raise DataDownloadError()

    def rollback(self):
        logger.info(_("Rollback!Remove the not complete file {}").format(self.dst_file))
        os.remove(self.dst_file)

    @classmethod
    def get_start(cls, dst_dir: str):
        dones = os.listdir(dst_dir)
        if dones:
            current = max(dones)
            return datetime.datetime.strptime(current, "%Y%m%d" + TARFILETYPE) + relativedelta(days=+1)
        else:
            return START_DATE


class TarStreamRequest(RawStreamRequest):
    def __init__(self, date: datetime.datetime, url: str, dst_dir: str):
        self.FILENAME = date.strftime("%Y%m%d") + '.csv.gz'
        super(TarStreamRequest, self).__init__(url, dst_dir)


class SymbolsStreamRequest(RawStreamRequest):
    FILENAME = INSTRUMENT_FILENAME

    @classmethod
    def get_start(cls, dst_dir: str):
        return datetime.datetime.utcnow() + relativedelta(days=-1, hour=0, minute=0, second=0, microsecond=0)


class _CsvStreamRequest(StreamRequest, _DownloadProcess):
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

    def __init__(self, date: datetime.datetime, url: str, cache_num: int = 100, chunk_process: bool = False,
                 csv_reader=csv.DictReader):
        super(_CsvStreamRequest, self).__init__()
        self.date = date
        self.url = url
        self.cache_num = cache_num
        self.chunk_process = chunk_process
        self.data = bytearray()
        self.cache = list()
        self.csv_reader = csv_reader
        self.dec = zlib.decompressobj(32 + zlib.MAX_WBITS)

    def setup(self):
        raise NotImplementedError

    def stream_decompress_requests(self):
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

    def process(self):
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

    def rollback(self):
        pass

    def cleanup(self):
        pass

    def process_chunk(self):
        raise NotImplementedError

    def process_row(self, row):
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
    fieldnames = list()

    def __init__(self, dst_dir: str, *args, **kwargs):
        super(_FileStream, self).__init__(chunk_process=False, *args, **kwargs)
        assert os.path.isdir(dst_dir)
        new_dir = os.path.join(dst_dir, self.date.strftime("%Y%m%d"))
        self.dst_dir = new_dir
        self.csv_file_writers = CsvFileDefaultDict(self.dst_dir, self.fieldnames)

    def setup(self):
        if not os.path.exists(self.dst_dir):
            os.mkdir(self.dst_dir)

    def process_row(self, row: dict):
        writer = self.csv_file_writers[row['symbol']]
        writer.writerow(row)
        return row

    def rollback(self):
        logger.info(_("Rollback : Remove the not complete dir {}").format(self.dst_dir))
        self.csv_file_writers.close()
        shutil.rmtree(self.dst_dir)

    def cleanup(self):
        self.csv_file_writers.close()

    @classmethod
    def get_start(cls, dst_dir: str):
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

    def __init__(self, dst_dir: str, *args, **kwargs):
        super(_ZipFileStream, self).__init__(dst_dir, *args, **kwargs)
        self.csv_file_writers = CsvZipDefaultDict(self.dst_dir, self.fieldnames)  # type: CsvZipDefaultDict

    def process_row(self, row: dict):
        f = self.csv_file_writers[row['symbol']]
        row_tuple = [row.get(key, self.DEFAULT) for key in self.fieldnames]
        self.csv_file_writers.writerow(f, row_tuple)


class TradeZipFileStream(_ZipFileStream):
    fieldnames = ["timestamp", "symbol", "side", "size", "price", "tickDirection", "trdMatchID", "grossValue",
                  "homeNotional", "foreignNotional"]


class QuoteZipFileStream(_ZipFileStream):
    fieldnames = ["timestamp", "symbol", "bidSize", "bidPrice", "askPrice", "askSize"]
