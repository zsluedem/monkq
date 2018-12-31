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
from MonkTrader.exchange.bitmex.data.quote import RawStreamRequest, QuoteMongoStream, TradeMongoStream, QuoteFileStream, \
    TradeFileStream
from MonkTrader.utils import is_aware_datetime
from MonkTrader.exception import DataDownloadException
import tempfile
import zlib
import datetime
import random
import pytz
import os
import mongomock
import pytest

stream_b = b"""c1,c2,c3,c4
1,2,3,4
5,6,7,8"""

stream_s = stream_b.decode('utf8')

mock_url = 'http://mock.com'

stream_quote = b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:04.778522000,ADAZ18,256089,9.54e-06,9.55e-06,524060
2018-12-05D00:00:05.045590000,XBTUSD,256081,9.54e-06,9.55e-06,544060
2018-12-05D00:00:07.302458000,XBTZ18,256083,9.54e-06,9.55e-06,574060
"""

stream_quote_s = stream_quote.decode('utf8')

stream_quote = zlib.compress(stream_quote)

stream_trade = b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,ADAZ18,Sell,166774,9.54e-06,MinusTick,498350a3-8c03-affd-cf87-e6d8a90b70e5,159102396,166774,1.591024
2018-12-05D00:00:25.948313000,XBTUSD,Sell,11,9.54e-06,ZeroMinusTick,1d004a95-44fa-c75c-47cd-d651ecd41c25,10494,11,0.00010494
2018-12-05D00:00:25.948313000,XBTZ18,Sell,10000,9.54e-06,ZeroMinusTick,214aa626-cb6a-054f-ccf5-da4e14b5fd23,9540000,10000,0.0954
"""
stream_trade_s = stream_trade.decode('utf8')
stream_trade = zlib.compress(stream_trade)


def _mock_stream(self, url: str):
    s = 0
    while 1:
        ori = s
        s += random.randint(0, 10)

        yield self._stream[ori:s]

        if s > len(self._stream):
            break


class MockRawStreamRequest(RawStreamRequest):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockRawStreamRequest, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockQuoteMongoStream(QuoteMongoStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockQuoteMongoStream, self).__init__(*args, **kwargs)
        self._cli = mongomock.MongoClient()

    _stream_requests = _mock_stream


class MockTradeMongoStream(TradeMongoStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockTradeMongoStream, self).__init__(*args, **kwargs)
        self._cli = mongomock.MongoClient()

    _stream_requests = _mock_stream


class MockQuoteFileStream(QuoteFileStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockQuoteFileStream, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockTradeFileStream(TradeFileStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockTradeFileStream, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


def test_raw_stream_request():
    with tempfile.TemporaryDirectory() as tmp:
        date = datetime.datetime(2018, 1, 1)
        outcome = os.path.join(tmp, date.strftime("%Y%m%d") + RawStreamRequest.FILETYPE)
        stream = MockRawStreamRequest(date, mock_url, tmp, stream=stream_b)
        stream.process()

        with open(outcome, 'rb') as f:
            content = f.read()

        assert content == stream_b


def test_raw_stream_request_exception():
    with tempfile.TemporaryDirectory() as tmp:
        date = datetime.datetime(2018, 1, 1)
        outcome = os.path.join(tmp, date.strftime("%Y%m%d") + RawStreamRequest.FILETYPE)
        stream = MockRawStreamRequest(date, mock_url, tmp, stream=stream_s)
        with pytest.raises(DataDownloadException):
            stream.process()

        assert not os.path.exists(outcome)


def test_quote_mongo_stream():
    d = datetime.datetime(2018, 1, 1)

    stream = MockQuoteMongoStream(d, mock_url, stream=stream_quote)

    stream.process()

    obj = stream._cli.bitmex.quote.find_one({'symbol': "ADAZ18", "askSize": 524060})
    assert obj['bidSize'] == 256089
    assert obj['bidPrice'] == 9.54e-06
    assert obj['askPrice'] == 9.55e-06
    assert obj['timestamp'] == datetime.datetime(2018, 12, 5, 0, 0, 4, 778000)

    obj = stream._cli.bitmex.quote.find_one({'symbol': "XBTUSD", "askSize": 544060})
    assert obj['bidSize'] == 256081
    assert obj['bidPrice'] == 9.54e-06
    assert obj['askPrice'] == 9.55e-06
    assert obj['timestamp'] == datetime.datetime(2018, 12, 5, 0, 0, 5, 45000)

    obj = stream._cli.bitmex.quote.find_one({'symbol': "XBTZ18", "askSize": 574060})
    assert obj['bidSize'] == 256083
    assert obj['bidPrice'] == 9.54e-06
    assert obj['askPrice'] == 9.55e-06
    assert obj['timestamp'] == datetime.datetime(2018, 12, 5, 0, 0, 7, 302000)


def test_quote_mongo_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    stream = MockQuoteMongoStream(d, mock_url, stream=stream_quote_s)
    with pytest.raises(DataDownloadException):
        stream.process()

    obj = stream._cli.bitmex.quote.find_one({'symbol': "ADAZ18", "askSize": 524060})
    assert obj is None
    obj = stream._cli.bitmex.quote.find_one({'symbol': "XBTUSD", "askSize": 544060})
    assert obj is None
    obj = stream._cli.bitmex.quote.find_one({'symbol': "XBTZ18", "askSize": 574060})
    assert obj is None


def test_trade_mongo_stream():
    d = datetime.datetime(2018, 1, 1)

    stream = MockTradeMongoStream(d, mock_url, stream=stream_trade)

    stream.process()

    obj = stream._cli.bitmex.trade.find_one({'symbol': "ADAZ18", "trdMatchID": "498350a3-8c03-affd-cf87-e6d8a90b70e5"})
    assert obj['timestamp'] == datetime.datetime(2018, 12, 5, 0, 0, 25, 948000)
    assert obj['side'] == "Sell"
    assert obj['size'] == 166774
    assert obj['price'] == 9.54e-06
    assert obj['tickDirection'] == 'MinusTick'
    assert obj['grossValue'] == 159102396
    assert obj['homeNotional'] == 166774
    assert obj['foreignNotional'] == 1.591024

    obj = stream._cli.bitmex.trade.find_one({'symbol': "XBTUSD", "trdMatchID": "1d004a95-44fa-c75c-47cd-d651ecd41c25"})
    assert obj['timestamp'] == datetime.datetime(2018, 12, 5, 0, 0, 25, 948000)
    assert obj['side'] == "Sell"
    assert obj['size'] == 11
    assert obj['price'] == 9.54e-06
    assert obj['tickDirection'] == 'ZeroMinusTick'
    assert obj['grossValue'] == 10494
    assert obj['homeNotional'] == 11
    assert obj['foreignNotional'] == 0.00010494

    obj = stream._cli.bitmex.trade.find_one({'symbol': "XBTZ18", "trdMatchID": "214aa626-cb6a-054f-ccf5-da4e14b5fd23"})
    assert obj['timestamp'] == datetime.datetime(2018, 12, 5, 0, 0, 25, 948000)
    assert obj['side'] == "Sell"
    assert obj['size'] == 10000
    assert obj['price'] == 9.54e-06
    assert obj['tickDirection'] == 'ZeroMinusTick'
    assert obj['grossValue'] == 9540000
    assert obj['homeNotional'] == 10000
    assert obj['foreignNotional'] == 0.0954


def test_trade_mongo_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    stream = MockTradeMongoStream(d, mock_url, stream=stream_trade_s)
    with pytest.raises(DataDownloadException):
        stream.process()

    obj = stream._cli.bitmex.trade.find_one(
        {'symbol': "ADAZ18", "trdMatchID": "498350a3-8c03-affd-cf87-e6d8a90b70e5,159102396"})
    assert obj is None
    obj = stream._cli.bitmex.trade.find_one({'symbol': "XBTUSD", "trdMatchID": "1d004a95-44fa-c75c-47cd-d651ecd41c25"})
    assert obj is None
    obj = stream._cli.bitmex.trade.find_one({'symbol': "XBTZ18", "trdMatchID": "214aa626-cb6a-054f-ccf5-da4e14b5fd23"})
    assert obj is None

def test_trade_file_stream():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockTradeFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_trade)

        stream.process()

        with open(os.path.join(tar_dir, "ADAZ18.csv")) as f:
            content = f.read()
            assert content == """timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,ADAZ18,Sell,166774,9.54e-06,MinusTick,498350a3-8c03-affd-cf87-e6d8a90b70e5,159102396,166774,1.591024
"""
        with open(os.path.join(tar_dir, "XBTUSD.csv")) as f:
            content = f.read()
            assert content == """timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,XBTUSD,Sell,11,9.54e-06,ZeroMinusTick,1d004a95-44fa-c75c-47cd-d651ecd41c25,10494,11,0.00010494
"""

        with open(os.path.join(tar_dir, "XBTZ18.csv")) as f:
            content = f.read()
            assert content == """timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,XBTZ18,Sell,10000,9.54e-06,ZeroMinusTick,214aa626-cb6a-054f-ccf5-da4e14b5fd23,9540000,10000,0.0954
"""


def test_trade_file_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockTradeFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_trade_s)

        with pytest.raises(DataDownloadException):
            stream.process()

        assert not os.path.exists(tar_dir)

def test_quote_file_stream():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockQuoteFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_quote)

        stream.process()

        with open(os.path.join(tar_dir, "ADAZ18.csv")) as f:
            content = f.read()
            assert content == """timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:04.778522000,ADAZ18,256089,9.54e-06,9.55e-06,524060
"""
        with open(os.path.join(tar_dir, "XBTUSD.csv")) as f:
            content = f.read()
            assert content == """timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:05.045590000,XBTUSD,256081,9.54e-06,9.55e-06,544060
"""

        with open(os.path.join(tar_dir, "XBTZ18.csv")) as f:
            content = f.read()
            assert content == """timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:07.302458000,XBTZ18,256083,9.54e-06,9.55e-06,574060
"""
def test_quote_file_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockQuoteFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_quote_s)

        with pytest.raises(DataDownloadException):
            stream.process()

        assert not os.path.exists(tar_dir)

