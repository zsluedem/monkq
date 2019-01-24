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
import json
import time

import pytest
from aiohttp import web
from MonkTrader.exchange.bitmex.exchange import BitmexExchange
from MonkTrader.utils import get_resource_path


def instrument_handler(request: web.Request):
    with open(get_resource_path('active_instrument.json')) as f:
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
        "content-length": "39192"
    }
    return web.Response(body=body, headers=headers)


async def order_handler(request: web.Request):
    if request.method == "GET":
        params = await request.json()
        assert json.loads(params['filter']).get('open')
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
            "content-length": "706"
        }
        body = """[{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "",
        "account": 142643,"symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3200,
        "displayQty": null,"stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD",
        "settlCurrency": "XBt","ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "",
        "contingencyType": "","exDestination": "XBME","ordStatus": "New","triggered": "","workingIndicator": true,
        "ordRejReason": "","simpleLeavesQty": null,"leavesQty": 100,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Submitted via API.",
        "transactTime": "2019-01-23T02:01:46.849Z","timestamp": "2019-01-23T02:01:46.849Z"}]"""
    elif request.method == "POST":
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
            "content-length": "704"
        }
        body = """{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "","account": 142643,
        "symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3200,"displayQty": null,
        "stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD","settlCurrency": "XBt",
        "ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "","contingencyType": "",
        "exDestination": "XBME","ordStatus": "New","triggered": "","workingIndicator": true,"ordRejReason": "",
        "simpleLeavesQty": null,"leavesQty": 100,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Submitted via API.",
        "transactTime": "2019-01-23T02:01:46.849Z","timestamp": "2019-01-23T02:01:46.849Z"}"""
    elif request.method == "PUT":
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
            "content-length": "737"
        }
        body = """{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "","account": 142643,
        "symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3300,"displayQty": null,
        "stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD","settlCurrency": "XBt",
        "ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "","contingencyType": "",
        "exDestination": "XBME","ordStatus": "New","triggered": "","workingIndicator": true,"ordRejReason": "",
        "simpleLeavesQty": null,"leavesQty": 100,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Amended price: Amended via API.\nSubmitted via API.",
        "transactTime": "2019-01-23T02:24:19.745Z","timestamp": "2019-01-23T02:24:19.745Z"}"""
    elif request.method == "DELETE":
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
            "content-length": "739"
        }
        body = """[{"orderID": "7fe1fbe3-4756-cabd-1f9e-74f862fba392","clOrdID": "","clOrdLinkID": "","account": 142643,
        "symbol": "XBTUSD","side": "Buy","simpleOrderQty": null,"orderQty": 100,"price": 3300,"displayQty": null,
        "stopPx": null,"pegOffsetValue": null,"pegPriceType": "","currency": "USD","settlCurrency": "XBt",
        "ordType": "Limit","timeInForce": "GoodTillCancel","execInst": "","contingencyType": "",
        "exDestination": "XBME","ordStatus": "Canceled","triggered": "","workingIndicator": false,"ordRejReason": "",
        "simpleLeavesQty": null,"leavesQty": 0,"simpleCumQty": null,"cumQty": 0,"avgPx": null,
        "multiLegReportingType": "SingleSecurity","text": "Canceled: Canceled via API.\nSubmitted via API.",
        "transactTime": "2019-01-23T02:24:19.745Z","timestamp": "2019-01-23T02:26:49.958Z"}]"""
    else:
        assert False
    return web.Response(body=body, headers=headers)


@pytest.fixture(scope='module')
async def normal_bitmex_server(aiohttp_server):
    app = web.Application()
    app.router.add_get('/instrument', instrument_handler)
    app.router.add_get('/order', instrument_handler)

    server = await aiohttp_server(app)
    yield server


async def test_bitmex_exchange():
    exchange = BitmexExchange()

    order_id = await exchange.place_limit_order('XBTUSD', 3200, 100)

    await exchange.amend_order(order_id=order_id, price=3300)

    await exchange.cancel_order(order_id=order_id)

    await exchange.place_market_order("XBTUSD", 100)

    await exchange.get_last_price("XBTUSD")

    await exchange.available_instruments()

    await exchange.get_kline("XBTUSD")

    await exchange.get_recent_trades("XBTUSD")