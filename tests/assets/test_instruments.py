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
from typing import TypeVar

from dateutil.tz import tzutc
from MonkTrader.assets import AbcExchange
from MonkTrader.assets.instrument import FutureInstrument, Instrument

T_EXCHANGE = TypeVar('T_EXCHANGE', bound="AbcExchange")

up_raw_data = {
    "symbol": "XBT7D_U105",
    "rootSymbol": "XBT",
    "state": "Open",
    "typ": "OCECCS",
    "listing": "2018-12-28T12:00:00.000Z",
    "front": "2018-12-28T12:00:00.000Z",
    "expiry": "2019-01-04T12:00:00.000Z",
    "settle": "2019-01-04T12:00:00.000Z",
    "relistInterval": "2000-01-08T00:00:00.000Z",
    "inverseLeg": "",
    "sellLeg": "",
    "buyLeg": "",
    "optionStrikePcnt": 1.05,
    "optionStrikeRound": 250,
    "optionStrikePrice": 3750,
    "optionMultiplier": -0.1,
    "positionCurrency": "",
    "underlying": "XBT",
    "quoteCurrency": "XBT",
    "underlyingSymbol": "XBT=",
    "reference": "BMEX",
    "referenceSymbol": ".BXBT30M",
    "calcInterval": None,
    "publishInterval": None,
    "publishTime": None,
    "maxOrderQty": 10000000,
    "maxPrice": 0.1,
    "lotSize": 1,
    "tickSize": 0.00001,
    "multiplier": 100000000,
    "settlCurrency": "XBt",
    "underlyingToPositionMultiplier": 10,
    "underlyingToSettleMultiplier": None,
    "quoteToSettleMultiplier": 100000000,
    "isQuanto": False,
    "isInverse": False,
    "initMargin": 1,
    "maintMargin": 0,
    "riskLimit": None,
    "riskStep": None,
    "limit": None,
    "capped": True,
    "taxed": True,
    "deleverage": True,
    "makerFee": 0,
    "takerFee": 0,
    "settlementFee": 0,
    "insuranceFee": 0,
    "fundingBaseSymbol": "",
    "fundingQuoteSymbol": "",
    "fundingPremiumSymbol": "",
    "fundingTimestamp": None,
    "fundingInterval": None,
    "fundingRate": None,
    "indicativeFundingRate": None,
    "rebalanceTimestamp": None,
    "rebalanceInterval": None,
    "openingTimestamp": "2019-01-03T08:00:00.000Z",
    "closingTimestamp": "2019-01-03T09:00:00.000Z",
    "sessionInterval": "2000-01-01T01:00:00.000Z",
    "prevClosePrice": 0.06,
    "limitDownPrice": 0,
    "limitUpPrice": 0.1,
    "bankruptLimitDownPrice": None,
    "bankruptLimitUpPrice": None,
    "prevTotalVolume": 7507,
    "totalVolume": 7507,
    "volume": 0,
    "volume24h": 0,
    "prevTotalTurnover": 75070000000,
    "totalTurnover": 75070000000,
    "turnover": 0,
    "turnover24h": 0,
    "homeNotional24h": 0,
    "foreignNotional24h": 0,
    "prevPrice24h": 0.06,
    "vwap": None,
    "highPrice": None,
    "lowPrice": None,
    "lastPrice": 0.06,
    "lastPriceProtected": 0.00423,
    "lastTickDirection": "PlusTick",
    "lastChangePcnt": 0,
    "bidPrice": 0.03172,
    "midPrice": 0.04586,
    "askPrice": 0.06,
    "impactBidPrice": 0.00480572,
    "impactMidPrice": 0.032405,
    "impactAskPrice": 0.06,
    "hasLiquidity": False,
    "openInterest": 374,
    "openValue": 3740000000,
    "fairMethod": "",
    "fairBasisRate": 0,
    "fairBasis": 0,
    "fairPrice": 0.00257,
    "markMethod": "LastPrice",
    "markPrice": 0.06,
    "indicativeTaxRate": 0,
    "indicativeSettlePrice": 0.00257,
    "optionUnderlyingPrice": 3848.73,
    "settledPrice": None,
    "timestamp": "2019-01-03T08:27:40.000Z"
}
down_raw_data = {
    "symbol": "XBT7D_D95",
    "rootSymbol": "XBT",
    "state": "Open",
    "typ": "OPECCS",
    "listing": "2018-12-28T12:00:00.000Z",
    "front": "2018-12-28T12:00:00.000Z",
    "expiry": "2019-01-04T12:00:00.000Z",
    "settle": "2019-01-04T12:00:00.000Z",
    "relistInterval": "2000-01-08T00:00:00.000Z",
    "inverseLeg": "",
    "sellLeg": "",
    "buyLeg": "",
    "optionStrikePcnt": 0.95,
    "optionStrikeRound": 250,
    "optionStrikePrice": 3500,
    "optionMultiplier": -0.1,
    "positionCurrency": "",
    "underlying": "XBT",
    "quoteCurrency": "XBT",
    "underlyingSymbol": "XBT=",
    "reference": "BMEX",
    "referenceSymbol": ".BXBT30M",
    "calcInterval": None,
    "publishInterval": None,
    "publishTime": None,
    "maxOrderQty": 10000000,
    "maxPrice": 0.1,
    "lotSize": 1,
    "tickSize": 0.00001,
    "multiplier": 100000000,
    "settlCurrency": "XBt",
    "underlyingToPositionMultiplier": 10,
    "underlyingToSettleMultiplier": None,
    "quoteToSettleMultiplier": 100000000,
    "isQuanto": False,
    "isInverse": False,
    "initMargin": 1,
    "maintMargin": 0,
    "riskLimit": None,
    "riskStep": None,
    "limit": None,
    "capped": True,
    "taxed": True,
    "deleverage": True,
    "makerFee": 0,
    "takerFee": 0,
    "settlementFee": 0,
    "insuranceFee": 0,
    "fundingBaseSymbol": "",
    "fundingQuoteSymbol": "",
    "fundingPremiumSymbol": "",
    "fundingTimestamp": None,
    "fundingInterval": None,
    "fundingRate": None,
    "indicativeFundingRate": None,
    "rebalanceTimestamp": None,
    "rebalanceInterval": None,
    "openingTimestamp": "2019-01-03T08:00:00.000Z",
    "closingTimestamp": "2019-01-03T09:00:00.000Z",
    "sessionInterval": "2000-01-01T01:00:00.000Z",
    "prevClosePrice": 0.09,
    "limitDownPrice": 0,
    "limitUpPrice": 0.1,
    "bankruptLimitDownPrice": None,
    "bankruptLimitUpPrice": None,
    "prevTotalVolume": 399,
    "totalVolume": 399,
    "volume": 0,
    "volume24h": 0,
    "prevTotalTurnover": 3990000000,
    "totalTurnover": 3990000000,
    "turnover": 0,
    "turnover24h": 0,
    "homeNotional24h": 0,
    "foreignNotional24h": 0,
    "prevPrice24h": 0.09,
    "vwap": None,
    "highPrice": None,
    "lowPrice": None,
    "lastPrice": 0.09,
    "lastPriceProtected": 0.00336,
    "lastTickDirection": "PlusTick",
    "lastChangePcnt": 0,
    "bidPrice": 0.00517,
    "midPrice": 0.047585,
    "askPrice": 0.09,
    "impactBidPrice": None,
    "impactMidPrice": None,
    "impactAskPrice": None,
    "hasLiquidity": False,
    "openInterest": 1,
    "openValue": 10000000,
    "fairMethod": "",
    "fairBasisRate": 0,
    "fairBasis": 0,
    "fairPrice": 0,
    "markMethod": "LastPrice",
    "markPrice": 0.09,
    "indicativeTaxRate": 0,
    "indicativeSettlePrice": 0,
    "optionUnderlyingPrice": 3848.73,
    "settledPrice": None,
    "timestamp": "2019-01-03T08:27:40.000Z"
}
perpetual_raw_data = {
    "symbol": "XBTUSD",
    "rootSymbol": "XBT",
    "state": "Open",
    "typ": "FFWCSX",
    "listing": "2016-05-04T12:00:00.000Z",
    "front": "2016-05-04T12:00:00.000Z",
    "expiry": None,
    "settle": None,
    "relistInterval": None,
    "inverseLeg": "",
    "sellLeg": "",
    "buyLeg": "",
    "optionStrikePcnt": None,
    "optionStrikeRound": None,
    "optionStrikePrice": None,
    "optionMultiplier": None,
    "positionCurrency": "USD",
    "underlying": "XBT",
    "quoteCurrency": "USD",
    "underlyingSymbol": "XBT=",
    "reference": "BMEX",
    "referenceSymbol": ".BXBT",
    "calcInterval": None,
    "publishInterval": None,
    "publishTime": None,
    "maxOrderQty": 10000000,
    "maxPrice": 1000000,
    "lotSize": 1,
    "tickSize": 0.5,
    "multiplier": -100000000,
    "settlCurrency": "XBt",
    "underlyingToPositionMultiplier": None,
    "underlyingToSettleMultiplier": -100000000,
    "quoteToSettleMultiplier": None,
    "isQuanto": False,
    "isInverse": True,
    "initMargin": 0.01,
    "maintMargin": 0.005,
    "riskLimit": 20000000000,
    "riskStep": 10000000000,
    "limit": None,
    "capped": False,
    "taxed": True,
    "deleverage": True,
    "makerFee": -0.00025,
    "takerFee": 0.00075,
    "settlementFee": 0,
    "insuranceFee": 0,
    "fundingBaseSymbol": ".XBTBON8H",
    "fundingQuoteSymbol": ".USDBON8H",
    "fundingPremiumSymbol": ".XBTUSDPI8H",
    "fundingTimestamp": "2019-01-03T12:00:00.000Z",
    "fundingInterval": "2000-01-01T08:00:00.000Z",
    "fundingRate": -0.00375,
    "indicativeFundingRate": -0.00375,
    "rebalanceTimestamp": None,
    "rebalanceInterval": None,
    "openingTimestamp": "2019-01-03T08:00:00.000Z",
    "closingTimestamp": "2019-01-03T09:00:00.000Z",
    "sessionInterval": "2000-01-01T01:00:00.000Z",
    "prevClosePrice": 3809.65,
    "limitDownPrice": None,
    "limitUpPrice": None,
    "bankruptLimitDownPrice": None,
    "bankruptLimitUpPrice": None,
    "prevTotalVolume": 102168738552,
    "totalVolume": 102169329238,
    "volume": 590686,
    "volume24h": 26991613,
    "prevTotalTurnover": 1493455449583993,
    "totalTurnover": 1493470976643893,
    "turnover": 15527059900,
    "turnover24h": 707812523487,
    "homeNotional24h": 7078.1252348700145,
    "foreignNotional24h": 26991613,
    "prevPrice24h": 3783,
    "vwap": 3813.4462,
    "highPrice": 3900,
    "lowPrice": 3755,
    "lastPrice": 3816.5,
    "lastPriceProtected": 3816.5,
    "lastTickDirection": "ZeroPlusTick",
    "lastChangePcnt": 0.0089,
    "bidPrice": 3816.5,
    "midPrice": 3816.75,
    "askPrice": 3817,
    "impactBidPrice": 3805.0302,
    "impactMidPrice": 3813.25,
    "impactAskPrice": 3821.4613,
    "hasLiquidity": True,
    "openInterest": 79094182,
    "openValue": 2058505180732,
    "fairMethod": "FundingRate",
    "fairBasisRate": -4.10625,
    "fairBasis": -6.37,
    "fairPrice": 3842.36,
    "markMethod": "FairPrice",
    "markPrice": 3842.36,
    "indicativeTaxRate": 0,
    "indicativeSettlePrice": 3848.73,
    "optionUnderlyingPrice": None,
    "settledPrice": None,
    "timestamp": "2019-01-03T08:28:10.000Z"
}


future_raw_date = {
    "symbol": "TRXH19",
    "rootSymbol": "TRX",
    "state": "Open",
    "typ": "FFCCSX",
    "listing": "2018-12-12T06:00:00.000Z",
    "front": "2019-02-22T12:00:00.000Z",
    "expiry": "2019-03-29T12:00:00.000Z",
    "settle": "2019-03-29T12:00:00.000Z",
    "relistInterval": None,
    "inverseLeg": "",
    "sellLeg": "",
    "buyLeg": "",
    "optionStrikePcnt": None,
    "optionStrikeRound": None,
    "optionStrikePrice": None,
    "optionMultiplier": None,
    "positionCurrency": "TRX",
    "underlying": "TRX",
    "quoteCurrency": "XBT",
    "underlyingSymbol": "TRXXBT=",
    "reference": "BMEX",
    "referenceSymbol": ".TRXXBT30M",
    "calcInterval": None,
    "publishInterval": None,
    "publishTime": None,
    "maxOrderQty": 100000000,
    "maxPrice": 10,
    "lotSize": 1,
    "tickSize": 1e-8,
    "multiplier": 100000000,
    "settlCurrency": "XBt",
    "underlyingToPositionMultiplier": 1,
    "underlyingToSettleMultiplier": None,
    "quoteToSettleMultiplier": 100000000,
    "isQuanto": False,
    "isInverse": False,
    "initMargin": 0.05,
    "maintMargin": 0.025,
    "riskLimit": 5000000000,
    "riskStep": 5000000000,
    "limit": None,
    "capped": False,
    "taxed": True,
    "deleverage": True,
    "makerFee": -0.0005,
    "takerFee": 0.0025,
    "settlementFee": 0,
    "insuranceFee": 0,
    "fundingBaseSymbol": "",
    "fundingQuoteSymbol": "",
    "fundingPremiumSymbol": "",
    "fundingTimestamp": None,
    "fundingInterval": None,
    "fundingRate": None,
    "indicativeFundingRate": None,
    "rebalanceTimestamp": None,
    "rebalanceInterval": None,
    "openingTimestamp": "2019-01-03T08:00:00.000Z",
    "closingTimestamp": "2019-01-03T09:00:00.000Z",
    "sessionInterval": "2000-01-01T01:00:00.000Z",
    "prevClosePrice": 0.00000539,
    "limitDownPrice": None,
    "limitUpPrice": None,
    "bankruptLimitDownPrice": None,
    "bankruptLimitUpPrice": None,
    "prevTotalVolume": 46281925,
    "totalVolume": 46319438,
    "volume": 37513,
    "volume24h": 3117765,
    "prevTotalTurnover": 24105753373,
    "totalTurnover": 24125785326,
    "turnover": 20031953,
    "turnover24h": 1665174249,
    "homeNotional24h": 3117765,
    "foreignNotional24h": 16.65174249,
    "prevPrice24h": 0.00000527,
    "vwap": 0.00000535,
    "highPrice": 0.00000543,
    "lowPrice": 0.00000528,
    "lastPrice": 0.00000533,
    "lastPriceProtected": 0.00000533,
    "lastTickDirection": "MinusTick",
    "lastChangePcnt": 0.0114,
    "bidPrice": 0.00000532,
    "midPrice": 0.000005325,
    "askPrice": 0.00000533,
    "impactBidPrice": 0.00000532,
    "impactMidPrice": 0.000005325,
    "impactAskPrice": 0.00000533,
    "hasLiquidity": True,
    "openInterest": 12139132,
    "openValue": 6470157356,
    "fairMethod": "ImpactMidPrice",
    "fairBasisRate": 0.2,
    "fairBasis": 2.4e-7,
    "fairPrice": 0.00000533,
    "markMethod": "FairPrice",
    "markPrice": 0.00000533,
    "indicativeTaxRate": 0,
    "indicativeSettlePrice": 0.00000509,
    "optionUnderlyingPrice": None,
    "settledPrice": None,
    "timestamp": "2019-01-03T08:28:14.100Z"
}

test_instrument_keymap = {
    'symbol': 'symbol',
    'listing': 'listing_date',
    'expiry': 'expiry_date',
    'underlying': 'underlying',
    "quoteCurrency":'quote_currency',
    'lotSize':'lot_size',
    'tickSize':'tick_size',
    'makerFee': 'maker_fee',
    'takerFee': 'taker_fee',
}

test_future_instrument_keymap = {
    'symbol': 'symbol',
    'listing': 'listing_date',
    'expiry': 'expiry_date',
    'underlying': 'underlying',
    "quoteCurrency":'quote_currency',
    'lotSize':'lot_size',
    'tickSize':'tick_size',
    'makerFee': 'maker_fee',
    'takerFee': 'taker_fee',

    'initMargin':'init_margin_rate',
    'maintMargin': 'maint_margin_rate',

    'settlementFee': 'settlement_fee',
    'settlCurrency': 'settle_currency',

    'settle': 'settle_date',
    'front': 'front_date',
    'referenceSymbol': 'reference_symbol',
    'deleverage': 'deleverage',

    'rootSymbol': 'root_symbol'
}


def test_instrument(exchange: T_EXCHANGE) -> None:
    instrument = Instrument.create(test_instrument_keymap, {
        'symbol': 'RHOC',
        'listing': '2018-12-28T12:00:00.000Z',
        'expiry': '2018-12-30T12:00:00.000Z',
        'underlying': 'XBT',
        'quoteCurrency': "XBT",
        'lotSize': 1,
        'tickSize': .00001,
        'makerFee': .005,
        'takerFee': .005,
    }, exchange)

    assert instrument.symbol == "RHOC"
    assert instrument.listing_date == datetime.datetime(2018,12,28,12,tzinfo=tzutc())
    assert instrument.expiry_date == datetime.datetime(2018,12,30,12,tzinfo=tzutc())
    assert instrument.underlying == 'XBT'
    assert instrument.quote_currency == 'XBT'
    assert instrument.lot_size == 1
    assert instrument.tick_size == 0.00001
    assert instrument.maker_fee == 0.005
    assert instrument.taker_fee == 0.005
    assert instrument.exchange == exchange


def test_future_instrument(exchange: T_EXCHANGE) -> None:
    instrument = FutureInstrument.create(test_future_instrument_keymap, future_raw_date, exchange)
    assert instrument.symbol == "TRXH19"
    assert instrument.listing_date == datetime.datetime(2018, 12, 12, 6, tzinfo=tzutc())
    assert instrument.expiry_date == datetime.datetime(2019, 3, 29, 12, tzinfo=tzutc())
    assert instrument.underlying == 'TRX'
    assert instrument.quote_currency == 'XBT'
    assert instrument.lot_size == 1
    assert instrument.tick_size == 1e-8
    assert instrument.maker_fee == -0.0005
    assert instrument.taker_fee == 0.0025

    assert instrument.root_symbol == 'TRX'
    assert instrument.init_margin_rate == 0.05
    assert instrument.maint_margin_rate == 0.025
    assert instrument.settlement_fee == 0
    assert instrument.settle_currency == 'XBt'
    assert instrument.settle_date == datetime.datetime(2019, 3, 29, 12, tzinfo=tzutc())
    assert instrument.front_date == datetime.datetime(2019, 2, 22, 12, tzinfo=tzutc())
    assert instrument.reference_symbol == '.TRXXBT30M'
    assert instrument.deleverage == True
    assert instrument.exchange == exchange

# test_upside_instrument_keymap = {
#
# }
#
# test_downside_instrument_keymap = {
#
# }
#
# test_perpetual_instrument_keymap = {
#
# }



# def test_downside_instrument():
#     pass
#
#
# def test_upside_instrument():
#     pass
#
#
# def test_perpetual_instrument():
#     pass
