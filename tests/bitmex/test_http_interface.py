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
import asyncio
import json
import ssl
import time
from typing import Callable, Coroutine
from unittest.mock import patch

import pytest
from aiohttp import ClientSession, TCPConnector, web  # type:ignore
from aiohttp.test_utils import TestServer
from MonkTrader.exception import (
    AuthError, HttpAuthError, HttpError, MarginNotEnoughError, MaxRetryError,
    NotFoundError, RateLimitError,
)
from MonkTrader.exchange.bitmex.http import BitMexHTTPInterface
from tests.tools import get_resource_path

TEST_API_KEY = "ae86vJ85yU8Mh5r6iSv68asb"
TEST_API_SECRET = "Yl39dzyn5YzuswQ_7qGtEx1LxxnwV5dM2Ex1ihr_EK-4Rs8b"

TIMEOUT = 3


@pytest.fixture()  # type:ignore
async def normal_bitmex_server(
        aiohttp_server: Callable[[web.Application], Coroutine[TestServer, None, None]]) -> TestServer:
    def instrument_handler(request: web.Request) -> web.Response:
        if request.query.get('symbol') == 'XBTUSD':
            body = """[{"symbol": "XBTUSD","rootSymbol": "XBT","state": "Open","typ": "FFWCSX",
            "listing": "2016-05-04T12:00:00.000Z","front": "2016-05-04T12:00:00.000Z","expiry": null,"settle": null,
            "relistInterval": null,"inverseLeg": "","sellLeg": "","buyLeg": "","optionStrikePcnt": null,
            "optionStrikeRound": null,"optionStrikePrice": null,"optionMultiplier": null,"positionCurrency": "USD",
            "underlying": "XBT","quoteCurrency": "USD","underlyingSymbol": "XBT=","reference": "BMEX",
            "referenceSymbol": ".BXBT","calcInterval": null,"publishInterval": null,"publishTime": null,
            "maxOrderQty": 10000000,"maxPrice": 1000000,"lotSize": 1,"tickSize": 0.5,"multiplier": -100000000,
            "settlCurrency": "XBt","underlyingToPositionMultiplier": null,"underlyingToSettleMultiplier": -100000000,
            "quoteToSettleMultiplier": null,"isQuanto": false,"isInverse": true,"initMargin": 0.01,
            "maintMargin": 0.005,"riskLimit": 20000000000,"riskStep": 10000000000,"limit": null,"capped": false,
            "taxed": true,"deleverage": true,"makerFee": -0.00025,"takerFee": 0.00075,"settlementFee": 0,
            "insuranceFee": 0,"fundingBaseSymbol": ".XBTBON8H","fundingQuoteSymbol": ".USDBON8H",
            "fundingPremiumSymbol": ".XBTUSDPI8H","fundingTimestamp": "2019-01-26T20:00:00.000Z",
            "fundingInterval": "2000-01-01T08:00:00.000Z","fundingRate": -0.001936,"indicativeFundingRate": -0.00375,
            "rebalanceTimestamp": null,"rebalanceInterval": null,"openingTimestamp": "2019-01-26T13:00:00.000Z",
            "closingTimestamp": "2019-01-26T14:00:00.000Z","sessionInterval": "2000-01-01T01:00:00.000Z",
            "prevClosePrice": 3586.54,"limitDownPrice": null,"limitUpPrice": null,"bankruptLimitDownPrice": null,
            "bankruptLimitUpPrice": null,"prevTotalVolume": 102941917787,"totalVolume": 102942050207,"volume": 132420,
            "volume24h": 21824599,"prevTotalTurnover": 1514270738123941,"totalTurnover": 1514274456624001,
            "turnover": 3718500060,"turnover24h": 611598052793,"homeNotional24h": 6115.9805279300135,
            "foreignNotional24h": 21824599,"prevPrice24h": 3564,"vwap": 3568.4973,"highPrice": 3640,"lowPrice": 3535.5,
            "lastPrice": 3561,"lastPriceProtected": 3561,"lastTickDirection": "MinusTick","lastChangePcnt": -0.0008,
            "bidPrice": 3560.5,"midPrice": 3560.75,"askPrice": 3561,"impactBidPrice": 3560.1125,
            "impactMidPrice": 3561.5,"impactAskPrice": 3562.9031,"hasLiquidity": true,"openInterest": 70009145,
            "openValue": 1956195529590,"fairMethod": "FundingRate","fairBasisRate": -2.11992,"fairBasis": -5.67,
            "fairPrice": 3578.8,"markMethod":"FairPrice","markPrice": 3578.8,"indicativeTaxRate": 0,
            "indicativeSettlePrice": 3584.47,
            "optionUnderlyingPrice": null,"settledPrice": null,"timestamp": "2019-01-26T13:28:00.000Z"}]"""
        else:
            with open(get_resource_path('bitmex/active_instrument.json')) as f:
                active_contents = f.read()
            body = active_contents
        headers = {
            "date": "Tue, 22 Jan 2019 12:49:47 GMT",
            "etag": "W/\"9918-e7K8CpBi1vBK/P8xS2l5q9PEQsg\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": str(int(time.time())),
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        return web.Response(body=body, headers=headers)

    async def order_get_handler(request: web.Request) -> web.Response:
        params = request.query['filter']
        assert json.loads(params).get('open')
        headers = {
            "date": "Wed, 23 Jan 2019 02:03:34 GMT",
            "etag": "W/\"2c2-94e3x9W9j3T3qypOCnVuNZJEUmw\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": "1548209015",
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        body = """[{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "",
        "account": 142643,"symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3200,
        "displayQty": null,"stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD",
        "settlCurrency": "XBt","ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "",
        "contingencyType": "","exDestination": "XBME","ordStatus": "New","triggered": "","workingIndicator": true,
        "ordRejReason": "","simpleLeavesQty": null,"leavesQty": 100,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Submitted via API.",
        "transactTime": "2019-01-23T02:01:46.849Z","timestamp": "2019-01-23T02:01:46.849Z"}]"""
        return web.Response(text=body, headers=headers)

    async def order_post_handler(request: web.Request) -> web.Response:
        headers = {
            "date": "Wed, 23 Jan 2019 02:01:46 GMT",
            "etag": "W/\"2c0-n4ZDZgcW+jPzvDDtibem17Rjb7E\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": "1548208907",
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        body = """{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "","account": 142643,
        "symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3200,"displayQty": null,
        "stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD","settlCurrency": "XBt",
        "ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "","contingencyType": "",
        "exDestination": "XBME","ordStatus": "New","triggered": "","workingIndicator": true,"ordRejReason": "",
        "simpleLeavesQty": null,"leavesQty": 100,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Submitted via API.",
        "transactTime": "2019-01-23T02:01:46.849Z","timestamp": "2019-01-23T02:01:46.849Z"}"""

        return web.Response(body=body, headers=headers)

    async def order_put_handler(request: web.Request) -> web.Response:
        headers = {
            "date": "Wed, 23 Jan 2019 02:24:19 GMT",
            "etag": "W/\"2e1-FgU6zAWULAr8QvcDhZgaCXsd/lQ\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": "1548210260",
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        body = """{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "","account": 142643,
        "symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3300,"displayQty": null,
        "stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD","settlCurrency": "XBt",
        "ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "","contingencyType": "",
        "exDestination": "XBME","ordStatus": "New","triggered": "","workingIndicator": true,"ordRejReason": "",
        "simpleLeavesQty": null,"leavesQty": 100,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Amended price: Amended via API.Submitted via API.",
        "transactTime": "2019-01-23T02:24:19.745Z","timestamp": "2019-01-23T02:24:19.745Z"}"""
        return web.Response(body=body, headers=headers)

    async def order_delete_handler(request: web.Request) -> web.Response:
        headers = {
            "date": "Wed, 23 Jan 2019 02:26:49 GMT",
            "etag": "W/\"2e3-oHgYMl1OJnGKxsK7hKiHKVed4mM\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": "1548210410",
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        body = """[{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "","account": 142643,
        "symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3300,"displayQty": null,
        "stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD","settlCurrency": "XBt",
        "ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "","contingencyType": "",
        "exDestination": "XBME","ordStatus": "Canceled","triggered": "","workingIndicator": false,"ordRejReason": "",
        "simpleLeavesQty": null,"leavesQty": 0,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Canceled: Canceled via API.Submitted via API.",
        "transactTime": "2019-01-23T02:24:19.745Z","timestamp": "2019-01-23T02:26:49.958Z"}]"""
        return web.Response(body=body, headers=headers)

    async def trade_handler(request: web.Request) -> web.Response:
        body = """[{"timestamp": "2019-01-26T13:38:34.301Z","symbol": "XBTUSD","side": "Buy","size": 50,"price": 3559.5,
        "tickDirection": "ZeroPlusTick","trdMatchID": "105ac363-0abd-48c7-dce7-ce74abd0e838","grossValue": 1404700,
        "homeNotional": 0.014047,"foreignNotional": 50},{"timestamp": "2019-01-26T13:38:33.474Z","symbol": "XBTUSD",
        "side": "Buy","size": 1,"price": 3559.5,"tickDirection": "ZeroPlusTick","trdMatchID":
        "5a17cd5b-8019-6d41-6afe-7e59208496b9","grossValue": 28094,"homeNotional": 0.00028094,"foreignNotional": 1},
        {"timestamp": "2019-01-26T13:38:08.058Z","symbol": "XBTUSD","side": "Buy","size": 8,"price": 3559.5,
        "tickDirection": "PlusTick","trdMatchID": "daa57e03-15b3-dbc5-1de2-cb583fc8df0a","grossValue": 224752,
        "homeNotional": 0.00224752,"foreignNotional": 8}]"""
        headers = {
            "date": "Sat, 26 Jan 2019 13:38:41 GMT",
            "etag": "W/\"2dc-r004Wek/XxE+/PMnri8+xgiRW+Q\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": "1548509922",
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        return web.Response(body=body, headers=headers)

    async def trade_bucketed_handler(request: web.Request) -> web.Response:
        body = """[{"timestamp": "2019-01-26T13:39:00.000Z","symbol": "XBTUSD","open": 3559,"high": 3559.5,
        "low": 3559.5,"close": 3559.5,"trades": 3,"volume": 59,"vwap": 3559.5,"lastSize": 50,"turnover": 1657546,
        "homeNotional": 0.01657546,"foreignNotional": 59},{"timestamp": "2019-01-26T13:38:00.000Z","symbol": "XBTUSD",
        "open": 3559,"high": 3559.5,"low": 3559,"close": 3559,"trades": 4,"volume": 87,"vwap": 3559.4789,"lastSize": 3,
        "turnover": 2444190,"homeNotional": 0.024441900000000003,"foreignNotional": 87},
        {"timestamp": "2019-01-26T13:37:00.000Z","symbol": "XBTUSD","open": 3559.5,"high": 3559.5,"low": 3559,
        "close": 3559,"trades": 14,"volume": 4301,"vwap": 3559.4789,"lastSize": 4,"turnover": 120832310,
        "homeNotional": 1.2083230999999999,"foreignNotional": 4301}]"""
        headers = {
            "date": "Sat, 26 Jan 2019 13:40:14 GMT",
            "etag": "W/\"2ca-35VuwNdtBw1gaLSAWE/h3WXJwXI\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": "1548510015",
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        return web.Response(body=body, headers=headers)

    async def quote_handler(request: web.Response) -> web.Response:
        body = """[{"symbol": "XBTUSD","id": 15599644500,"side": "Sell","size": 2543,"price": 3555},
        {"symbol": "XBTUSD","id": 15599644550,"side": "Buy","size": 3433,"price": 3554.5}]"""
        headers = {
            "date": "Sat, 26 Jan 2019 16:02:48 GMT",
            "etag": "W/\"9a-ak85nWtrZnW3uMGRCF/UHm2y+YE\"",
            "x-powered-by": "Profit",
            "x-ratelimit-remaining": "149",
            "content-type": "application/json; charset=utf-8",
            "status": "200",
            "x-ratelimit-reset": "1548518569",
            "x-ratelimit-limit": "150",
            "strict-transport-security": "max-age=31536000; includeSubDomains",
        }
        return web.Response(body=body, headers=headers)

    app = web.Application()
    app.router.add_get('/instrument', instrument_handler)
    app.router.add_get('/instrument/active', instrument_handler)
    app.router.add_get('/order', order_get_handler)
    app.router.add_post('/order', order_post_handler)
    app.router.add_put('/order', order_put_handler)
    app.router.add_delete('/order', order_delete_handler)
    app.router.add_get('/trade', trade_handler)
    app.router.add_get('/trade/bucketed', trade_bucketed_handler)
    app.router.add_get('/orderBook/L2', quote_handler)
    server = await aiohttp_server(app)
    yield server


@pytest.fixture()  # type:ignore
async def abnormal_bitmex_server(
        aiohttp_server: Callable[[web.Application], Coroutine[TestServer, None, None]]) -> None:
    async def order_margin_not_enough(request: web.Request) -> web.Response:
        ret = {
            "error": {"message": "insufficient available balance",
                      "name": "margin"}
        }
        return web.json_response(ret, status=400)

    async def auth_error(request: web.Request) -> web.Response:
        ret = {
            "error": {"message": "auth error", "name": "auth"}
        }
        return web.json_response(ret, status=401)

    async def http_403(request: web.Request) -> web.Response:
        ret = {
            "error": {"message": "403", "name": "403"}
        }
        return web.json_response(ret, status=403)

    async def http_404(request: web.Request) -> web.Response:
        ret = {
            "error": {"message": "404", "name": "404"}
        }
        return web.json_response(ret, status=404)

    async def rate_limit(request: web.Request) -> web.Response:
        ret = {
            "error": {"message": "rate limit", "name": "rate"}
        }
        headers = {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": str(int(time.time()) + 3000),
            "x-ratelimit-limit": "150",
        }
        return web.json_response(data=ret, status=429, headers=headers)

    async def http_503(request: web.Request) -> web.Response:
        return web.Response(status=503)

    async def other_error(request: web.Request) -> web.Response:
        return web.Response(status=500)

    async def timeout_error(request: web.Request) -> web.Response:
        await asyncio.sleep(TIMEOUT * 2)
        return web.Response(body="[]")

    app = web.Application()
    app.router.add_post('/order', order_margin_not_enough)
    app.router.add_put('/order', auth_error)
    app.router.add_get('/order', http_403)
    app.router.add_delete('/order', http_404)
    app.router.add_get('/instrument', rate_limit)
    app.router.add_get('/instrument/active', timeout_error)
    app.router.add_get('/trade', http_503)
    app.router.add_get('/trade/bucketed', other_error)

    server = await aiohttp_server(app)
    yield server


async def test_bitmex_http_interface(normal_bitmex_server: TestServer, loop: asyncio.AbstractEventLoop) -> None:
    with patch("MonkTrader.exchange.bitmex.http.BITMEX_TESTNET_API_URL",
               'http://127.0.0.1:{}/'.format(normal_bitmex_server.port)):
        ssl_context = ssl.create_default_context()
        connector = TCPConnector(keepalive_timeout=90)  # type:ignore
        session = ClientSession(loop=loop, connector=connector)

        exchange = BitMexHTTPInterface({'API_KEY': TEST_API_KEY, "API_SECRET": TEST_API_SECRET, "IS_TEST": True},
                                       connector, session, ssl_context, None, loop)
        symbol = "XBTUSD"

        await exchange.get_instrument_info(symbol)

        order_id = await exchange.place_limit_order('XBTUSD', 3200, 100)

        assert await exchange.amend_order(order_id=order_id, price=3300)

        assert await exchange.cancel_order(order_id=order_id)

        await exchange.place_market_order(symbol, 100)

        await exchange.open_orders_http()

        await exchange.active_instruments()

        await exchange.get_recent_trades(symbol, 3)

        await exchange.get_kline(symbol, "1m", 3)

        await exchange.session.close()


async def test_bitmex_http_interface_error(abnormal_bitmex_server: TestServer,
                                           loop: asyncio.AbstractEventLoop) -> None:
    with patch("MonkTrader.exchange.bitmex.http.BITMEX_API_URL",
               'http://127.0.0.1:{}/'.format(abnormal_bitmex_server.port)):
        ssl_context = ssl.create_default_context()
        connector = TCPConnector(keepalive_timeout=90)  # type:ignore
        session = ClientSession(loop=loop, connector=connector)

        http_interface = BitMexHTTPInterface(
            {'API_KEY': TEST_API_KEY, "API_SECRET": TEST_API_SECRET, "IS_TEST": False},
            connector, session, ssl_context, None, loop)

        symbol = "XBTUSD"
        with pytest.raises(MarginNotEnoughError):
            await http_interface.place_limit_order(symbol, 10, 100)

        with pytest.raises(HttpAuthError):
            await http_interface.amend_order("random", 10, 100)

        with pytest.raises(HttpError):
            await http_interface.open_orders_http()

        with pytest.raises(MaxRetryError):
            await http_interface.active_instruments(timeout=TIMEOUT)

        with pytest.raises(MaxRetryError):
            await http_interface.get_recent_trades(symbol)

        with pytest.raises(HttpError):
            await http_interface.get_kline(symbol, "1m")

        with pytest.raises(RateLimitError):
            await http_interface.get_instrument_info(symbol)

        with pytest.raises(NotFoundError):
            await http_interface.cancel_order("random")

        await http_interface.session.close()


async def test_bitmex_auth_error(loop: asyncio.AbstractEventLoop) -> None:
    ssl_context = ssl.create_default_context()
    connector = TCPConnector(keepalive_timeout=90)  # type:ignore
    session = ClientSession(loop=loop, connector=connector)

    http_interface = BitMexHTTPInterface({'IS_TEST': True}, connector, session, ssl_context, None, None)
    symbol = "XBTUSD"

    with pytest.raises(AuthError):
        await http_interface.place_limit_order(symbol, 10, 100)
