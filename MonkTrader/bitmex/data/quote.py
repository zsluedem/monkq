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
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from MonkTrader.logger import console_log
from MonkTrader.config import CONF

START_DATE = datetime.datetime(2014, 11, 22)
now = datetime.datetime.now() + relativedelta(days=-1)

trade_link = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/{}.csv.gz"
quote_link = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/quote/{}.csv.gz"

TARFILETYPE = '.csv.gz'

class CsvFileDefaultDict(defaultdict):
    def __init__(self, dir, fieldnames, *args, **kwargs):
        super(CsvFileDefaultDict, self).__init__(*args, **kwargs)
        self.dir = dir
        self.default_factory = csv.DictWriter
        self.fieldnames = fieldnames
        self.file_set = set()

    def __missing__(self, key):
        f = open(os.path.join(self.dir, f'{key}.csv'), 'w')
        self.file_set.add(f)
        ret = self[key] = self.default_factory(f, fieldnames=self.fieldnames)
        ret.writeheader()
        return ret

    def close(self):
        for f in self.file_set:
            f.close()


class StreamRequest():
    def _stream_requests(self, url):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=io.DEFAULT_BUFFER_SIZE):
            yield chunk

class TarStreamRequest(StreamRequest):
    def __init__(self, date:datetime.datetime, url:str, dst_dir:str):
        super(TarStreamRequest, self).__init__()
        self.date = date
        self.url = url
        assert os.path.isdir(dst_dir)
        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)
        self.dst_dir = dst_dir

        self.dst_file = os.path.join(self.dst_dir, self.date.strftime("%Y%m%d")+TARFILETYPE)

    def process(self):
        try:
            with open(self.dst_file, 'wb') as f:
                for chunk in self._stream_requests(self.url):
                    f.write(chunk)
        except Exception as e:
            console_log.exception(f"Exception #{e}# happened when process f{self.date} data")
            self.rollback()
            os._exit(1)

    def rollback(self):
        shutil.rmtree(self.dst_file, ignore_errors=True)

class CsvStreamRequest(StreamRequest):
    def __init__(self, date:datetime.datetime, url:str, cache_num:int=100, chunk_process:bool=False, csv_reader=csv.DictReader, decompress=False):
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
            console_log.exception(f"Exception {e} happened when process f{self.date} data")
            self.rollback()
            os._exit(-1)
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

    def setup(self):
        col = CONF.db['bitmex'][self.collection_name]
        col.create_index(self.index)

    def process_chunk(self):
        col = CONF.db['bitmex'][self.collection_name]
        col.insert_many(self.cache)

    def process_row(self, row):
        return row

    def rollback(self):
        col = CONF.db['bitmex'][self.collection_name]
        result = col.delete_many({'timestamp': {"$gte": self.date}})
        console_log.info(f"Rollback result: {result.raw_result}")


class QuoteMongoStream(MongoStream):
    collection_name = "quote"
    index = [("timestamp", pymongo.DESCENDING), ('symbol', pymongo.DESCENDING)]

    def process_row(self, row):
        row['timestamp'] = datetime.datetime.strptime(row['timestamp'][:26], '%Y-%m-%dD%H:%M:%S.%f')
        row['bidSize'] = float(row['bidSize']) if row['bidSize'] else 0
        row['bidPrice'] = float(row['bidPrice']) if row['bidPrice'] else 0
        row['askPrice'] = float(row['askPrice']) if row['askPrice'] else 0
        row['askSize'] = float(row['askSize']) if row['askSize'] else 0
        return row


class TradeMongoStream(MongoStream):
    collection_name = "trade"
    index = [("timestamp", pymongo.DESCENDING), ('symbol', pymongo.DESCENDING)]

    def process_row(self, row):
        row['timestamp'] = datetime.datetime.strptime(row['timestamp'][:26], '%Y-%m-%dD%H:%M:%S.%f')
        row['size'] = float(row['size']) if row['size'] else 0
        row['price'] = float(row['price']) if row['price'] else 0
        row['grossValue'] = float(row['grossValue']) if row['grossValue'] else 0
        row['foreignNotional'] = float(row['foreignNotional']) if row['foreignNotional'] else 0
        return row

class FileStream(CsvStreamRequest):
    fieldnames = list()

    def __init__(self, dst_dir, *args, **kwargs):
        super(FileStream, self).__init__(chunk_process=False, *args, **kwargs)
        assert os.path.isdir(dst_dir)
        new_dir = os.path.join(dst_dir, self.date.strftime("%Y%m%d"))
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        self.dst_dir = new_dir
        self.csv_file_writers = CsvFileDefaultDict(self.dst_dir, self.fieldnames)

    def setup(self):
        pass

    def process_row(self, row):
        writer = self.csv_file_writers[row['symbol']]
        writer.writerow(row)
        return row

    def rollback(self):
        shutil.rmtree(self.dst_dir, ignore_errors=True)

    def cleanup(self):
        self.csv_file_writers.close()

class TradeFileStream(FileStream):
    fieldnames = ["timestamp","symbol","side","size","price","tickDirection","trdMatchID","grossValue","homeNotional","foreignNotional"]

class QuoteFileStream(FileStream):
    fieldnames = ["timestamp","symbol","bidSize","bidPrice","askPrice","askSize"]


# class Recover():
#     def setup(self):
#         pass
#
#     def get_checkpoint(self):
#         pass
#
#     def recover(self):
#         start = self.get_checkpoint()
#         for date in rrule(freq=DAILY, dtstart=start, until=now):
#             console_log.info(f'Downloading {kind} data on {date.isoformat()}')
#             downloader:CsvStreamRequest= self.downloader(date, link.format(date.strftime("%Y%m%d")))
#             downloader.process()
#             console_log.info(f'Finished downloading {kind} data on {date.isoformat()}')
#
# class MongoRecover(Recover):
#     def __init__(self, downloader, *args, **kwargs):
#         self.downloader = downloader
#
#     def get_checkpoint(self):
#         col = CONF.db['bitmex'][kind]
#         cur = col.find().sort("timestamp", pymongo.DESCENDING)
#         try:
#             item = cur.next()
#             start = item['timestamp'] + relativedelta(days=+1, hour=0, minute=0, second=0, microsecond=0)
#         except StopIteration:
#             console_log.info('There is no data in the database. We are going to start download data from scratch')
#             start = START_DATE
#         return start
#
#
# class CsvFileRecover(Recover):



def save_history(kind, mode, dst_dir):
    console_log.info('Start downloading the data')
    if kind == 'quote':
        link = quote_link
        if mode == 'csv':
            Streamer = QuoteFileStream
        elif mode == 'tar':
            Streamer = TarStreamRequest
        elif mode == 'mongo':
            Streamer = QuoteMongoStream
        else:
            raise ValueError
    elif kind == 'trade':
        link = trade_link
        if mode == 'csv':
            Streamer = TradeFileStream
        elif mode == 'tar':
            Streamer = TarStreamRequest
        elif mode == 'mongo':
            Streamer = TradeMongoStream
        else:
            raise ValueError
    else:
        raise ValueError

    if mode == 'mongo':
        col = CONF.db['bitmex'][kind]
        cur = col.find().sort("timestamp", pymongo.DESCENDING)
        try:
            item = cur.next()
            start = item['timestamp'] + relativedelta(days=+1, hour=0, minute=0, second=0, microsecond=0)
        except StopIteration:
            console_log.info('There is no data in the database. We are going to start download data from scratch')
            start = START_DATE
    elif mode == 'csv':
        dones = os.listdir(dst_dir.exists)
        if dones:
            current= max(dones)
            start = datetime.datetime.strptime(current, "%Y%m%d") + relativedelta(days=+1)
        else:
            start = START_DATE
    elif mode == 'tar':
        dones = os.listdir(dst_dir.exists)
        if dones:
            current= max(dones)
            start = datetime.datetime.strptime(current, "%Y%m%d"+TARFILETYPE) + relativedelta(days=+1)
        else:
            start = START_DATE
    for date in rrule(freq=DAILY, dtstart=start, until=now):
        console_log.info(f'Downloading {kind} data on {date.isoformat()}')
        qstream = Streamer(date=date, url=link.format(date.strftime("%Y%m%d")), dst_dir=dst_dir.exists)
        qstream.process()
        console_log.info(f'Finished downloading {kind} data on {date.isoformat()}')
