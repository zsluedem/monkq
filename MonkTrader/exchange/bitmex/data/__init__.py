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
import os

import pymongo
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from dateutil.tz import tzutc
from logbook import Logger
from MonkTrader.config import settings
from MonkTrader.data import DataDownloader, Point, ProcessPoints
from MonkTrader.exchange.bitmex.const import (
    TARFILETYPE, quote_link, symbols_link, trade_link,
)
from MonkTrader.exchange.bitmex.data.download import (
    START_DATE, QuoteMongoStream, QuoteZipFileStream, SymbolsStreamRequest,
    TarStreamRequest, TradeMongoStream, TradeZipFileStream,
)

from ..log import logger_group

logger = Logger('exchange.bitmex.data')
logger_group.add_logger(logger)

class DatePoint(Point):
    def __init__(self, date: datetime.datetime):
        self.date = date

    def __eq__(self, other):
        assert isinstance(other, DatePoint)
        return self.date == other.date

    @property
    def value(self):
        return self.date


class BitMexProcessPoints(ProcessPoints):
    def __init__(self, start: datetime.datetime, end: datetime.datetime):
        self.start = start + relativedelta(hour=0, minute=0, second=0, microsecond=0)
        self.end = end + relativedelta(hour=0, minute=0, second=0, microsecond=0)
        self.current = start

        self.rruls_date = rrule(freq=DAILY, dtstart=self.start, until=self.end)

    def __iter__(self):
        for date in rrule(freq=DAILY, dtstart=self.start, until=self.end):
            yield DatePoint(date)

    def __next__(self):
        if self.current <= self.end:
            date = self.current
            self.current += relativedelta(days=1)
            return DatePoint(date)
        else:
            raise StopIteration()


class BitMexDownloader(DataDownloader):
    def __init__(self, kind: str, mode: str, dst_dir: str):
        logger.info('Start downloading the data')
        self.mode = mode
        self.kind = kind
        self.dst_dir = dst_dir
        self.init_kind(mode, kind)
        self.init_mode(mode, dst_dir, kind)

    def init_kind(self, mode: str, kind: str):
        if kind == 'quote':
            self.link = quote_link
            if mode == 'csv':
                Streamer = QuoteZipFileStream
            elif mode == 'tar':
                Streamer = TarStreamRequest
            elif mode == 'mongo':
                Streamer = QuoteMongoStream
            else:
                raise ValueError
        elif kind == 'trade':
            self.link = trade_link
            if mode == 'csv':
                Streamer = TradeZipFileStream
            elif mode == 'tar':
                Streamer = TarStreamRequest
            elif mode == 'mongo':
                Streamer = TradeMongoStream
            else:
                raise ValueError
        elif kind == 'instruments':
            self.link = symbols_link
            Streamer = SymbolsStreamRequest
        else:
            raise ValueError()
        self.Streamer = Streamer  # type: Type[StreamRequest]

    def init_mode(self, mode: str, dst_dir: str, kind: str):
        self.end = datetime.datetime.utcnow() + relativedelta(days=-1, hour=0, minute=0, second=0, microsecond=0)
        if kind == 'instruments':
            self.start = datetime.datetime.utcnow() + relativedelta(days=-1, hour=0, minute=0, second=0, microsecond=0)
            return
        if mode == 'mongo':
            cli = pymongo.MongoClient(settings.DATABASE_URI)
            col = cli['bitmex'][kind]
            cur = col.find().sort("timestamp", pymongo.DESCENDING)
            try:
                item = cur.next()
                self.start = item['timestamp'] + relativedelta(days=+1, hour=0, minute=0, second=0, microsecond=0)
            except StopIteration:
                logger.info(
                    'There is no data in the database. We are going to self.star download data from scratch')
                self.start = START_DATE
        elif mode == 'csv':
            dones = os.listdir(dst_dir)
            if dones:
                current = max(dones)
                self.start = datetime.datetime.strptime(current, "%Y%m%d") + relativedelta(days=+1)
            else:
                self.start = START_DATE
        elif mode == 'tar':
            dones = os.listdir(dst_dir)
            if dones:
                current = max(dones)
                self.start = datetime.datetime.strptime(current, "%Y%m%d" + TARFILETYPE) + relativedelta(days=+1)
            else:
                self.start = START_DATE
        else:
            raise ValueError

    def process_point(self) -> BitMexProcessPoints:
        return BitMexProcessPoints(self.start, self.end)

    def download_one_point(self, point: DatePoint) -> None:
        logger.info('Downloading {} data on {}'.format(self.kind, point.value.isoformat()))
        qstream = self.Streamer(date=point.value, url=self.link.format(point.value.strftime("%Y%m%d")),
                                dst_dir=self.dst_dir)
        qstream.process()
        logger.info('Finished downloading {} data on {}'.format(self.kind, point.value.isoformat()))
