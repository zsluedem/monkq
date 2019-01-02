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
from MonkTrader.exchange.bitmex.data.quote import TarStreamRequest, QuoteMongoStream, TradeMongoStream, QuoteFileStream, \
    TradeFileStream, SymbolsStreamRequest, TradeZipFileStream, QuoteZipFileStream
from MonkTrader.exchange.bitmex.data import DatePoint, BitMexProcessPoints, BitMexDownloader, START_DATE

from MonkTrader.exception import DataDownloadException
from dateutil.relativedelta import relativedelta
import tempfile
import zlib
import datetime
import random
import pytz
import gzip
import os
import pytest

stream_b = b"""c1,c2,c3,c4
1,2,3,4
5,6,7,8"""

mock_url = 'http://mock.com'

stream_quote = b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:04.778522000,ADAZ18,256089,9.54e-06,9.55e-06,524060
2018-12-05D00:00:05.045590000,XBTUSD,256081,9.54e-06,9.55e-06,544060
2018-12-05D00:00:07.302458000,XBTZ18,256083,9.54e-06,9.55e-06,574060
"""

stream_quote = zlib.compress(stream_quote)

stream_trade = b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,ADAZ18,Sell,166774,9.54e-06,MinusTick,498350a3-8c03-affd-cf87-e6d8a90b70e5,159102396,166774,1.591024
2018-12-05D00:00:25.948313000,XBTUSD,Sell,11,9.54e-06,ZeroMinusTick,1d004a95-44fa-c75c-47cd-d651ecd41c25,10494,11,0.00010494
2018-12-05D00:00:25.948313000,XBTZ18,Sell,10000,9.54e-06,ZeroMinusTick,214aa626-cb6a-054f-ccf5-da4e14b5fd23,9540000,10000,0.0954
"""
stream_trade = zlib.compress(stream_trade)

stream_symbols = b"""[{"symbol": "XRPH19", "rootSymbol": "XRP", "state": "Open", "typ": "FFCCSX", "listing": "2018-12-17T04:00:00.000Z", "front": "2019-02-22T12:00:00.000Z", "expiry": "2019-03-29T12:00:00.000Z", "settle": "2019-03-29T12:00:00.000Z", "relistInterval": null, "inverseLeg": "", "sellLeg": "", "buyLeg": "", "optionStrikePcnt": null, "optionStrikeRound": null, "optionStrikePrice": null, "optionMultiplier": null, "positionCurrency": "XRP", "underlying": "XRP", "quoteCurrency": "XBT", "underlyingSymbol": "XRPXBT=", "reference": "BMEX", "referenceSymbol": ".BXRPXBT30M", "calcInterval": null, "publishInterval": null, "publishTime": null, "maxOrderQty": 100000000, "maxPrice": 10, "lotSize": 1, "tickSize": 1e-08, "multiplier": 100000000, "settlCurrency": "XBt", "underlyingToPositionMultiplier": 1, "underlyingToSettleMultiplier": null, "quoteToSettleMultiplier": 100000000, "isQuanto": false, "isInverse": false, "initMargin": 0.05, "maintMargin": 0.025, "riskLimit": 5000000000, "riskStep": 5000000000, "limit": null, "capped": false, "taxed": true, "deleverage": true, "makerFee": -0.0005, "takerFee": 0.0025, "settlementFee": 0, "insuranceFee": 0, "fundingBaseSymbol": "", "fundingQuoteSymbol": "", "fundingPremiumSymbol": "", "fundingTimestamp": null, "fundingInterval": null, "fundingRate": null, "indicativeFundingRate": null, "rebalanceTimestamp": null, "rebalanceInterval": null, "openingTimestamp": "2019-01-01T03:00:00.000Z", "closingTimestamp": "2019-01-01T04:00:00.000Z", "sessionInterval": "2000-01-01T01:00:00.000Z", "prevClosePrice": 9.42e-05, "limitDownPrice": null, "limitUpPrice": null, "bankruptLimitDownPrice": null, "bankruptLimitUpPrice": null, "prevTotalVolume": 238952605, "totalVolume": 239002688, "volume": 50083, "volume24h": 15443438, "prevTotalTurnover": 2319660919392, "totalTurnover": 2320132688566, "turnover": 471769174, "turnover24h": 146188755488, "homeNotional24h": 15443438, "foreignNotional24h": 1461.887554879999, "prevPrice24h": 9.505e-05, "vwap": 9.467e-05, "highPrice": 9.54e-05, "lowPrice": 9.401e-05, "lastPrice": 9.428e-05, "lastPriceProtected": 9.428e-05, "lastTickDirection": "ZeroPlusTick", "lastChangePcnt": -0.0081, "bidPrice": 9.434e-05, "midPrice": 9.435e-05, "askPrice": 9.436e-05, "impactBidPrice": 9.434e-05, "impactMidPrice": 9.437e-05, "impactAskPrice": 9.44e-05, "hasLiquidity": true, "openInterest": 32517836, "openValue": 306675711316, "fairMethod": "ImpactMidPrice", "fairBasisRate": 0.01, "fairBasis": 2.3e-07, "fairPrice": 9.431e-05, "markMethod": "FairPrice", "markPrice": 9.431e-05, "indicativeTaxRate": 0, "indicativeSettlePrice": 9.408e-05, "optionUnderlyingPrice": null, "settledPrice": null, "timestamp": "2019-01-01T03:22:50.000Z"}, {"symbol": "BCHH19", "rootSymbol": "BCH", "state": "Open", "typ": "FFCCSX", "listing": "2018-12-17T04:00:00.000Z", "front": "2019-02-22T12:00:00.000Z", "expiry": "2019-03-29T12:00:00.000Z", "settle": "2019-03-29T12:00:00.000Z", "relistInterval": null, "inverseLeg": "", "sellLeg": "", "buyLeg": "", "optionStrikePcnt": null, "optionStrikeRound": null, "optionStrikePrice": null, "optionMultiplier": null, "positionCurrency": "BCH", "underlying": "BCH", "quoteCurrency": "XBT", "underlyingSymbol": "BCHXBT=", "reference": "BMEX", "referenceSymbol": ".BBCHXBT30M", "calcInterval": null, "publishInterval": null, "publishTime": null, "maxOrderQty": 100000000, "maxPrice": 10, "lotSize": 1, "tickSize": 0.0001, "multiplier": 100000000, "settlCurrency": "XBt", "underlyingToPositionMultiplier": 1, "underlyingToSettleMultiplier": null, "quoteToSettleMultiplier": 100000000, "isQuanto": false, "isInverse": false, "initMargin": 0.05, "maintMargin": 0.025, "riskLimit": 5000000000, "riskStep": 5000000000, "limit": null, "capped": false, "taxed": true, "deleverage": true, "makerFee": -0.0005, "takerFee": 0.0025, "settlementFee": 0, "insuranceFee": 0, "fundingBaseSymbol": "", "fundingQuoteSymbol": "", "fundingPremiumSymbol": "", "fundingTimestamp": null, "fundingInterval": null, "fundingRate": null, "indicativeFundingRate": null, "rebalanceTimestamp": null, "rebalanceInterval": null, "openingTimestamp": "2019-01-01T03:00:00.000Z", "closingTimestamp": "2019-01-01T04:00:00.000Z", "sessionInterval": "2000-01-01T01:00:00.000Z", "prevClosePrice": 0.04083, "limitDownPrice": null, "limitUpPrice": null, "bankruptLimitDownPrice": null, "bankruptLimitUpPrice": null, "prevTotalVolume": 352014, "totalVolume": 353539, "volume": 1525, "volume24h": 27515, "prevTotalTurnover": 1477398180000, "totalTurnover": 1483686250000, "turnover": 6288070000, "turnover24h": 111226820000, "homeNotional24h": 27515, "foreignNotional24h": 1112.268200000001, "prevPrice24h": 0.0412, "vwap": 0.04042407, "highPrice": 0.0416, "lowPrice": 0.0388, "lastPrice": 0.0413, "lastPriceProtected": 0.0413, "lastTickDirection": "ZeroMinusTick", "lastChangePcnt": 0.0024, "bidPrice": 0.0413, "midPrice": 0.04135, "askPrice": 0.0414, "impactBidPrice": 0.0413, "impactMidPrice": 0.0414, "impactAskPrice": 0.04145715, "hasLiquidity": true, "openInterest": 24069, "openValue": 99645660000, "fairMethod": "ImpactMidPrice", "fairBasisRate": -0.06, "fairBasis": -0.0006, "fairPrice": 0.0414, "markMethod": "FairPrice", "markPrice": 0.0414, "indicativeTaxRate": 0, "indicativeSettlePrice": 0.042, "optionUnderlyingPrice": null, "settledPrice": null, "timestamp": "2019-01-01T03:22:50.000Z"}, {"symbol": "ADAH19", "rootSymbol": "ADA", "state": "Open", "typ": "FFCCSX", "listing": "2018-12-17T04:00:00.000Z", "front": "2019-02-22T12:00:00.000Z", "expiry": "2019-03-29T12:00:00.000Z", "settle": "2019-03-29T12:00:00.000Z", "relistInterval": null, "inverseLeg": "", "sellLeg": "", "buyLeg": "", "optionStrikePcnt": null, "optionStrikeRound": null, "optionStrikePrice": null, "optionMultiplier": null, "positionCurrency": "ADA", "underlying": "ADA", "quoteCurrency": "XBT", "underlyingSymbol": "ADAXBT=", "reference": "BMEX", "referenceSymbol": ".BADAXBT30M", "calcInterval": null, "publishInterval": null, "publishTime": null, "maxOrderQty": 100000000, "maxPrice": 10, "lotSize": 1, "tickSize": 1e-08, "multiplier": 100000000, "settlCurrency": "XBt", "underlyingToPositionMultiplier": 1, "underlyingToSettleMultiplier": null, "quoteToSettleMultiplier": 100000000, "isQuanto": false, "isInverse": false, "initMargin": 0.05, "maintMargin": 0.025, "riskLimit": 5000000000, "riskStep": 5000000000, "limit": null, "capped": false, "taxed": true, "deleverage": true, "makerFee": -0.0005, "takerFee": 0.0025, "settlementFee": 0, "insuranceFee": 0, "fundingBaseSymbol": "", "fundingQuoteSymbol": "", "fundingPremiumSymbol": "", "fundingTimestamp": null, "fundingInterval": null, "fundingRate": null, "indicativeFundingRate": null, "rebalanceTimestamp": null, "rebalanceInterval": null, "openingTimestamp": "2019-01-01T03:00:00.000Z", "closingTimestamp": "2019-01-01T04:00:00.000Z", "sessionInterval": "2000-01-01T01:00:00.000Z", "prevClosePrice": 1.1e-05, "limitDownPrice": null, "limitUpPrice": null, "bankruptLimitDownPrice": null, "bankruptLimitUpPrice": null, "prevTotalVolume": 416223681, "totalVolume": 416724252, "volume": 500571, "volume24h": 46652383, "prevTotalTurnover": 450215240966, "totalTurnover": 450761475947, "turnover": 546234981, "turnover24h": 51582221579, "homeNotional24h": 46652383, "foreignNotional24h": 515.82221579, "prevPrice24h": 1.124e-05, "vwap": 1.106e-05, "highPrice": 1.13e-05, "lowPrice": 1.088e-05, "lastPrice": 1.094e-05, "lastPriceProtected": 1.094e-05, "lastTickDirection": "ZeroPlusTick", "lastChangePcnt": -0.0267, "bidPrice": 1.093e-05, "midPrice": 1.0935e-05, "askPrice": 1.094e-05, "impactBidPrice": 1.093e-05, "impactMidPrice": 1.0945e-05, "impactAskPrice": 1.096e-05, "hasLiquidity": true, "openInterest": 44278456, "openValue": 48440630864, "fairMethod": "ImpactMidPrice", "fairBasisRate": 0.04, "fairBasis": 1e-07, "fairPrice": 1.094e-05, "markMethod": "FairPrice", "markPrice": 1.094e-05, "indicativeTaxRate": 0, "indicativeSettlePrice": 1.084e-05, "optionUnderlyingPrice": null, "settledPrice": null, "timestamp": "2019-01-01T03:22:25.000Z"}]"""


def _mock_stream(self, url: str):
    s = 0
    while 1:
        ori = s
        s += random.randint(0, 10)

        yield self._stream[ori:s]

        if s > len(self._stream):
            break


def _mock_exception_stream(self, url: str):
    s = 0
    while 1:
        ori = s
        s += random.randint(0, 10)

        yield self._stream[ori:s]

        if s > len(self._stream):
            raise Exception()


def test_datepoint():
    d = DatePoint(datetime.datetime(2018, 1, 1))
    assert d.value == datetime.datetime(2018, 1, 1)


def test_bitmex_process_points():
    p = BitMexProcessPoints(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 1, 5))
    assert next(p).value == datetime.datetime(2018, 1, 1)
    assert next(p).value == datetime.datetime(2018, 1, 2)
    assert next(p).value == datetime.datetime(2018, 1, 3)
    assert next(p).value == datetime.datetime(2018, 1, 4)
    assert next(p).value == datetime.datetime(2018, 1, 5)

    with pytest.raises(StopIteration):
        next(p)

    p_list = list(p)
    assert p_list[0] == DatePoint(datetime.datetime(2018, 1, 1))
    assert p_list[1] == DatePoint(datetime.datetime(2018, 1, 2))
    assert p_list[2] == DatePoint(datetime.datetime(2018, 1, 3))
    assert p_list[3] == DatePoint(datetime.datetime(2018, 1, 4))
    assert p_list[4] == DatePoint(datetime.datetime(2018, 1, 5))

    p2 = BitMexProcessPoints(datetime.datetime(2018, 1, 1), datetime.datetime(2018, 1, 1))
    assert next(p2).value == datetime.datetime(2018, 1, 1)
    with pytest.raises(StopIteration):
        next(p2)
    p2_list = list(p2)
    assert p2_list[0] == DatePoint(datetime.datetime(2018, 1, 1))
    with pytest.raises(IndexError):
        _ = p2_list[1]


def test_bitmex_downloader(bitmex_mongo):
    def mkfile(filename):
        with open(filename, 'w') as f:
            f.write('1')

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='quote', mode='csv', dst_dir=tmp)
        assert b.Streamer == QuoteFileStream
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103'))
        b = BitMexDownloader(kind='quote', mode='csv', dst_dir=tmp)
        assert b.Streamer == QuoteFileStream
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103'))
        b = BitMexDownloader(kind='trade', mode='csv', dst_dir=tmp)
        assert b.Streamer == TradeFileStream
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='trade', mode='csv', dst_dir=tmp)
        assert b.Streamer == TradeFileStream
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='symbols', mode='csv', dst_dir=tmp)
        assert b.Streamer == SymbolsStreamRequest
        assert b.start == b.end

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='trade', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == START_DATE

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103.csv.gz'))
        b = BitMexDownloader(kind='trade', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        mkfile(os.path.join(tmp, '20180103.csv.gz'))
        b = BitMexDownloader(kind='quote', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == datetime.datetime(2018, 1, 4)

    with tempfile.TemporaryDirectory() as tmp:
        b = BitMexDownloader(kind='quote', mode='tar', dst_dir=tmp)
        assert b.Streamer == TarStreamRequest
        assert b.start == START_DATE

    b = BitMexDownloader(kind='quote', mode='mongo', dst_dir=tmp)
    assert b.Streamer == QuoteMongoStream
    assert b.start == START_DATE

    b = BitMexDownloader(kind='trade', mode='mongo', dst_dir=tmp)
    assert b.Streamer == TradeMongoStream
    assert b.start == START_DATE

    bitmex_mongo.quote.insert({'timestamp': datetime.datetime(2018, 1, 3, 12)})
    b = BitMexDownloader(kind='quote', mode='mongo', dst_dir=tmp)
    assert b.Streamer == QuoteMongoStream
    assert b.start == datetime.datetime(2018, 1, 4)

    bitmex_mongo.trade.insert({'timestamp': datetime.datetime(2018, 1, 3, 12)})
    b = BitMexDownloader(kind='trade', mode='mongo', dst_dir=tmp)
    assert b.Streamer == TradeMongoStream
    assert b.start == datetime.datetime(2018, 1, 4)


class MockRawStreamRequest(TarStreamRequest):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockRawStreamRequest, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockQuoteMongoStream(QuoteMongoStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockQuoteMongoStream, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockTradeMongoStream(TradeMongoStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockTradeMongoStream, self).__init__(*args, **kwargs)

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


class MockTradeZipFileStream(TradeZipFileStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockTradeZipFileStream, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockQuoteZipFileStream(QuoteZipFileStream):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(MockQuoteZipFileStream, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


class MockSymbolsStream(SymbolsStreamRequest):
    def __init__(self, *args, **kwargs):
        self._stream = kwargs.pop('stream', '')
        super(SymbolsStreamRequest, self).__init__(*args, **kwargs)

    _stream_requests = _mock_stream


def test_symbols_stream_request():
    with tempfile.TemporaryDirectory() as tmp:
        stream = MockSymbolsStream(mock_url, tmp, stream=stream_symbols)
        stream.process()

        with open(os.path.join(tmp, 'symbols.json'), 'rb') as f:
            content = f.read()

        assert content == stream_symbols


def test_raw_stream_request():
    with tempfile.TemporaryDirectory() as tmp:
        date = datetime.datetime(2018, 1, 1)
        outcome = os.path.join(tmp, date.strftime("%Y%m%d") + '.csv.gz')
        stream = MockRawStreamRequest(date, mock_url, tmp, stream=stream_b)
        stream.process()

        with open(outcome, 'rb') as f:
            content = f.read()

        assert content == stream_b


def test_raw_stream_request_exception():
    with tempfile.TemporaryDirectory() as tmp:
        date = datetime.datetime(2018, 1, 1)
        outcome = os.path.join(tmp, date.strftime("%Y%m%d") + '.csv.gz')
        stream = MockRawStreamRequest(date, mock_url, tmp, stream=stream_b)
        stream._stream_requests = _mock_exception_stream
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

    stream = MockQuoteMongoStream(d, mock_url, stream=stream_quote)
    stream._stream_requests = _mock_exception_stream
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

    stream = MockTradeMongoStream(d, mock_url, stream=stream_trade)
    stream._stream_requests = _mock_exception_stream
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

        stream = MockTradeFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_trade)
        stream._stream_requests = _mock_exception_stream

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

        stream = MockQuoteFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_quote)
        stream._stream_requests = _mock_exception_stream

        with pytest.raises(DataDownloadException):
            stream.process()

        assert not os.path.exists(tar_dir)


def test_trade_zip_file_stream():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockTradeZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_trade)

        stream.process()

        with gzip.open(os.path.join(tar_dir, "ADAZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,ADAZ18,Sell,166774,9.54e-06,MinusTick,498350a3-8c03-affd-cf87-e6d8a90b70e5,159102396,166774,1.591024
"""
        with gzip.open(os.path.join(tar_dir, "XBTUSD.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,XBTUSD,Sell,11,9.54e-06,ZeroMinusTick,1d004a95-44fa-c75c-47cd-d651ecd41c25,10494,11,0.00010494
"""

        with gzip.open(os.path.join(tar_dir, "XBTZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,side,size,price,tickDirection,trdMatchID,grossValue,homeNotional,foreignNotional
2018-12-05D00:00:25.948313000,XBTZ18,Sell,10000,9.54e-06,ZeroMinusTick,214aa626-cb6a-054f-ccf5-da4e14b5fd23,9540000,10000,0.0954
"""


def test_trade_zip_file_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockTradeZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_trade)
        stream._stream_requests = _mock_exception_stream

        with pytest.raises(DataDownloadException):
            stream.process()

        assert not os.path.exists(tar_dir)


def test_quote_zip_file_stream():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockQuoteZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_quote)

        stream.process()

        with gzip.open(os.path.join(tar_dir, "ADAZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:04.778522000,ADAZ18,256089,9.54e-06,9.55e-06,524060
"""
        with gzip.open(os.path.join(tar_dir, "XBTUSD.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:05.045590000,XBTUSD,256081,9.54e-06,9.55e-06,544060
"""

        with gzip.open(os.path.join(tar_dir, "XBTZ18.csv.gz")) as f:
            content = f.read()
            assert content == b"""timestamp,symbol,bidSize,bidPrice,askPrice,askSize
2018-12-05D00:00:07.302458000,XBTZ18,256083,9.54e-06,9.55e-06,574060
"""


def test_quote_zip_file_stream_exception():
    d = datetime.datetime(2018, 1, 1)

    with tempfile.TemporaryDirectory() as tmp:
        tar_dir = os.path.join(tmp, d.strftime("%Y%m%d"))

        stream = MockQuoteZipFileStream(date=d, url=mock_url, dst_dir=tmp, stream=stream_quote)
        stream._stream_requests = _mock_exception_stream

        with pytest.raises(DataDownloadException):
            stream.process()

        assert not os.path.exists(tar_dir)
