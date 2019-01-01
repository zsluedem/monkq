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
from MonkTrader.utils import CsvFileDefaultDict, assure_dir
from MonkTrader.exception import DataDownloadException
from MonkTrader.exchange.bitmex.const import Bitmex_api_url
from urllib.parse import urljoin

from typing import Generator

START_DATE = datetime.datetime(2014, 11, 22) # bitmex open date

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

    def __init__(self, url: str, dst_dir: str, *args, **kwargs):
        super(SymbolsStreamRequest, self).__init__(url, dst_dir)


class CsvStreamRequest(StreamRequest):
    def __init__(self, date: datetime.datetime, url: str, cache_num: int = 100, chunk_process: bool = False,
                 csv_reader=csv.DictReader, decompress=False):
        super(CsvStreamRequest, self).__init__()
        self.date = date
        self.url = url
        self.cache_num = cache_num
        self.chunk_process = chunk_process
        self.data = bytearray()
        self.cache = list()
        self.csv_reader = csv_reader
        self.decompress = decompress
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


class MongoStream(CsvStreamRequest):
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


class FileStream(CsvStreamRequest):
    fieldnames = list()

    def __init__(self, dst_dir: str, *args, **kwargs):
        super(FileStream, self).__init__(chunk_process=False, *args, **kwargs)
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
        shutil.rmtree(self.dst_dir)

    def cleanup(self):
        self.csv_file_writers.close()


class TradeFileStream(FileStream):
    fieldnames = ["timestamp", "symbol", "side", "size", "price", "tickDirection", "trdMatchID", "grossValue",
                  "homeNotional", "foreignNotional"]


class QuoteFileStream(FileStream):
    fieldnames = ["timestamp", "symbol", "bidSize", "bidPrice", "askPrice", "askSize"]


