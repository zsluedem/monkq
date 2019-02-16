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
import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from logbook import Logger
from MonkTrader.data import DataDownloader, Point, ProcessPoints
from MonkTrader.exchange.bitmex.const import (
    QUOTE_LINK, SYMBOL_LINK, TRADE_LINK,
)
from MonkTrader.exchange.bitmex.data.download import (
    HDFQuoteStream, HDFTradeStream, QuoteZipFileStream, SymbolsStreamRequest,
    TarStreamRequest, TradeZipFileStream,
)
from MonkTrader.utils.i18n import _

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
        logger.info(_('Start downloading the data'))
        self.mode = mode
        self.kind = kind
        self.dst_dir = dst_dir
        self.init_kind(mode, kind)
        self.init_mode(dst_dir)

    def init_kind(self, mode: str, kind: str):
        if kind == 'quote':
            self.link = QUOTE_LINK
            if mode == 'csv':
                Streamer = QuoteZipFileStream
            elif mode == 'tar':
                Streamer = TarStreamRequest
            elif mode == 'hdf':
                Streamer = HDFQuoteStream
            else:
                raise ValueError
        elif kind == 'trade':
            self.link = TRADE_LINK
            if mode == 'csv':
                Streamer = TradeZipFileStream
            elif mode == 'tar':
                Streamer = TarStreamRequest
            elif mode == 'hdf':
                Streamer = HDFTradeStream
            else:
                raise ValueError
        elif kind == 'instruments':
            self.link = SYMBOL_LINK
            Streamer = SymbolsStreamRequest
        else:
            raise ValueError()
        self.Streamer = Streamer

    def init_mode(self, dst_dir: str):
        self.end = datetime.datetime.utcnow() + relativedelta(days=-1, hour=0, minute=0, second=0, microsecond=0)
        self.start = self.Streamer.get_start(dst_dir=dst_dir)

    def process_point(self) -> BitMexProcessPoints:
        return BitMexProcessPoints(self.start, self.end)

    def download_one_point(self, point: DatePoint) -> None:
        logger.info(_('Downloading {} data on {}').format(self.kind, point.value.isoformat()))
        qstream = self.Streamer(date=point.value, url=self.link.format(point.value.strftime("%Y%m%d")),
                                dst_dir=self.dst_dir, point=point)
        qstream.process()
        logger.info(_('Finished downloading {} data on {}').format(self.kind, point.value.isoformat()))
