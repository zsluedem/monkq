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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import datetime
import requests
import io
import zlib
import csv
import pymongo
import os
import shutil
from MonkTrader.logger import console_log
from MonkTrader.config import settings
from MonkTrader.utils import CsvFileDefaultDict, assure_dir, CsvZipDefaultDict
from MonkTrader.exception import DataDownloadException
from MonkTrader.exchange.bitmex.const import Bitmex_api_url
from urllib.parse import urljoin

from typing import Generator

START_DATE = datetime.datetime(2014, 11, 22)  # bitmex open date

trade_link = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/{}.csv.gz"
quote_link = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/quote/{}.csv.gz"
symbols_link = urljoin(Bitmex_api_url, "instrument")
TARFILETYPE = '.csv.gz'


class StreamRequest():
    def _stream_requests(self, url: str) -> Generator[bytes, None, None]:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=io.DEFAULT_BUFFER_SIZE):
            yield chunk

    def process(self):
        """
        process the data after the raw_process data
        :return:
        """
        raise NotImplementedError

    def rollback(self):
        """
        If there is anything wrong happening in the process, the whole process would rollback
        :return:
        """
        raise NotImplementedError


class RawStreamRequest(StreamRequest):
    """
    Stream a url request and save the raw contents to local.
    The child class has to be configured the `FILENAME`

    If anything exception happens in the process, the stream file would be deleted and raise `DataDownloadException`.

    :param url: the url used to stream, the url should be response content not just header.
    :param dst_dir: the content would save to the dst_dir directory with the `FILENAMe`.
    """
    FILENAME = None

    def __init__(self, url: str, dst_dir: str):
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
            console_log.exception("Exception #{}# happened when process {} {}".format(e, self.url, self.dst_file))
            raise DataDownloadException()

    def rollback(self):
        console_log.info("Remove the not complete file {}".format(self.dst_file))
        os.remove(self.dst_file)


class TarStreamRequest(RawStreamRequest):
    def __init__(self, date: datetime.datetime, url: str, dst_dir: str):
        self.FILENAME = date.strftime("%Y%m%d") + '.csv.gz'
        super(TarStreamRequest, self).__init__(url, dst_dir)


class SymbolsStreamRequest(RawStreamRequest):
    FILENAME = 'symbols.json'


class _CsvStreamRequest(StreamRequest):
    """
    A base class to process the stream a url request which would return a zip csv file.
    If any Exceptions happened in the process , the class would trigger `rollback` and raise `DataDownloadException` error.
    After all data are finished streaming, `cleanup` would trigger.

    The child class has to implement `setup`, `process_chunk`, `process_row`

    :param date: the date for the class to process
    :param url: use the url to stream the response to process
    :param cache_num: it worked with the param chunk_process ,if the chunk_process is True, the class would process the csv rows
        when the cached items reach to the cache_num
    :param chunk_process: If chunk_process is True , the class would process with cached items.Otherwise, it would process row by row.
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
        self.setup()
        try:
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
        except Exception as e:
            self.rollback()
            console_log.exception("Exception {} happened when process f{} data".format(e, self.date))
            raise DataDownloadException()
        self.cleanup()

    def rollback(self):
        pass

    def cleanup(self):
        pass

    def process_chunk(self):
        raise NotImplementedError

    def process_row(self, row):
        return row


class MongoStream(_CsvStreamRequest):
    """
    The class used to save the zip stream csv into MongoDB.
    The child class has to be configured the collection name and if you want to create an index for the collections, you
    have to configure the index, too.
    """
    collection_name = None
    index = None

    def __init__(self, *args, **kwargs):
        super(MongoStream, self).__init__(chunk_process=True, *args, **kwargs)
        self._cli = pymongo.MongoClient(settings.DATABASE_URI)

    def setup(self):
        col = self._cli['bitmex'][self.collection_name]
        col.create_index(self.index)

    def process_chunk(self):
        col = self._cli['bitmex'][self.collection_name]
        col.insert_many(self.cache)

    def process_row(self, row):
        return row

    def rollback(self):
        col = self._cli['bitmex'][self.collection_name]
        result = col.delete_many({'timestamp': {"$gte": self.date}})
        console_log.info("Rollback result: {}".format(result.raw_result))


class QuoteMongoStream(MongoStream):
    collection_name = "quote"
    index = [("timestamp", pymongo.DESCENDING), ('symbol', pymongo.DESCENDING)]

    def process_row(self, row: dict):
        row['timestamp'] = datetime.datetime.strptime(row['timestamp'][:26], '%Y-%m-%dD%H:%M:%S.%f')  # utc time
        row['bidSize'] = float(row['bidSize']) if row['bidSize'] else 0
        row['bidPrice'] = float(row['bidPrice']) if row['bidPrice'] else 0
        row['askPrice'] = float(row['askPrice']) if row['askPrice'] else 0
        row['askSize'] = float(row['askSize']) if row['askSize'] else 0
        return row


class TradeMongoStream(MongoStream):
    collection_name = "trade"
    index = [("timestamp", pymongo.DESCENDING), ('symbol', pymongo.DESCENDING)]

    def process_row(self, row):
        row['timestamp'] = datetime.datetime.strptime(row['timestamp'][:26], '%Y-%m-%dD%H:%M:%S.%f')  # utc time
        row['size'] = float(row['size']) if row['size'] else 0
        row['price'] = float(row['price']) if row['price'] else 0
        row['grossValue'] = float(row['grossValue']) if row['grossValue'] else 0
        row['foreignNotional'] = float(row['foreignNotional']) if row['foreignNotional'] else 0
        row['homeNotional'] = float(row['homeNotional']) if row['homeNotional'] else 0
        return row


class _FileStream(_CsvStreamRequest):
    """
    The child class which inherit this class has to be configured the filednames which are used to generate the csv headers.
    It takes a url and a destination directory to init and the class would stream the url response to several single files
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
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        self.dst_dir = new_dir
        self.csv_file_writers = CsvFileDefaultDict(self.dst_dir, self.fieldnames)

    def setup(self):
        pass

    def process_row(self, row: dict):
        writer = self.csv_file_writers[row['symbol']]
        writer.writerow(row)
        return row

    def rollback(self):
        console_log.info("Rollback : Remove the not complete dir {}".format(self.dst_dir))
        self.csv_file_writers.close()
        shutil.rmtree(self.dst_dir)

    def cleanup(self):
        self.csv_file_writers.close()


class TradeFileStream(_FileStream):
    fieldnames = ["timestamp", "symbol", "side", "size", "price", "tickDirection", "trdMatchID", "grossValue",
                  "homeNotional", "foreignNotional"]


class QuoteFileStream(_FileStream):
    fieldnames = ["timestamp", "symbol", "bidSize", "bidPrice", "askPrice", "askSize"]


class _ZipFileStream(_FileStream):
    """
    Instead of saving raw csv file in the directory, this class save a compressed csv into local to save storage.
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
