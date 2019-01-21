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
import json
import time
import warnings
from typing import List
from urllib.parse import urljoin

import pandas as pd
import pymongo
import requests
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from logbook import Logger
from requests.exceptions import ConnectTimeout

from MonkTrader.const import CHINA_CONNECT_TIMEOUT, CHINA_WARNING, MAX_HISTORY
from MonkTrader.exchange.bitmex.const import Bitmex_api_url
from ..log import logger_group

logger = Logger("exchange.bitmex.data")
logger_group.add_logger(logger)


def fetch_bitmex_symbols(active: bool = False):
    if active:
        url = urljoin(Bitmex_api_url, "instrument/active")
    else:
        url = urljoin(Bitmex_api_url, "instrument")
    try:
        req = requests.get(url, params={"count": 500}, timeout=CHINA_CONNECT_TIMEOUT)
    except ConnectTimeout:
        raise ConnectTimeout(CHINA_WARNING)
    body = json.loads(req.content)
    return body


def fetch_bitmex_kline(symbol: str, start_time: datetime.datetime, end_time: datetime.datetime, frequency: str):
    datas = list()
    while start_time < end_time:
        url = urljoin(Bitmex_api_url, "trade/bucketed")
        try:
            req = requests.get(url, params={"symbol": symbol, "binSize": frequency,
                                            "startTime": start_time.isoformat(),
                                            "endTime": end_time.isoformat(),
                                            "count": MAX_HISTORY}, timeout=CHINA_CONNECT_TIMEOUT)
        except ConnectTimeout:
            raise ConnectTimeout(CHINA_WARNING)
        # 防止频率过快被断连
        if req.status_code == 429:
            remaining = int(req.headers['x-ratelimit-remaining'])
            ratelimit_reset = req.headers['X-RateLimit-Reset']
            retry_after = float(req.headers['Retry-After'])
            warnings.warn(
                "Your rate is too fast and remaining is {}, retry after {}s, rate reset at {}".format(remaining,
                                                                                                      retry_after,
                                                                                                      ratelimit_reset))
            time.sleep(retry_after + 3)  # just sleep 3 more seconds to make safe
            continue
        elif req.status_code == 403:
            warnings.warn("Your frequency is so fast that they won't let you access.Just rest for a while")
            exit(1)

        klines = json.loads(req.content)
        if len(klines) == 0:
            break
        datas.extend(klines)
        start_time = parse(klines[-1].get("timestamp")) + relativedelta(second=+1)
    if len(datas) == 0:
        return None
    return datas


def to_json(datas: List):
    frame = pd.DataFrame(datas)
    frame['timestamp'] = pd.to_datetime(frame['timestamp'])
    return json.loads(frame.to_json(orient='records'))


def save_kline(db_cli: pymongo.MongoClient, frequency: str, active: bool = True):
    symbol_list = fetch_bitmex_symbols(active=active)
    symbol_list = symbol_list
    col = db_cli.bitmex[frequency]
    col.create_index(
        [("symbol", pymongo.ASCENDING), ("timestamp", pymongo.ASCENDING)], unique=True)

    end = datetime.datetime.now(tzutc()) + relativedelta(days=-1, hour=0, minute=0, second=0, microsecond=0)

    for index, symbol_info in enumerate(symbol_list):
        logger.info('The {} of Total {}'
                    .format(symbol_info['symbol'], len(symbol_list)))
        logger.info('DOWNLOAD PROGRESS {} '
                    .format(str(float(index / len(symbol_list) * 100))[0:4] + '%'))
        ref = col.find({"symbol": symbol_info['symbol']}).sort("timestamp", -1)

        if ref.count() > 0:
            start_stamp = ref.next()['timestamp'] / 1000
            start_time = datetime.datetime.fromtimestamp(start_stamp + 1, tz=tzutc())
            logger.info('UPDATE_SYMBOL {} Trying updating {} from {} to {}'.format(
                frequency, symbol_info['symbol'], start_time, end))
        else:
            start_time = symbol_info.get('listing', "2018-01-01T00:00:00Z")
            start_time = parse(start_time)
            logger.info('NEW_SYMBOL {} Trying downloading {} from {} to {}'.format(
                frequency, symbol_info['symbol'], start_time, end))

        data = fetch_bitmex_kline(symbol_info['symbol'],
                                  start_time, end, frequency)
        if data is None:
            logger.info('SYMBOL {} from {} to {} has no data'.format(
                symbol_info['symbol'], start_time, end))
            continue
        data = to_json(data)
        col.insert_many(data)


def save_symbols_mongo(db_cli: pymongo.MongoClient, active: bool):
    symbols = fetch_bitmex_symbols(active)
    col = db_cli.bitmex.symbols
    if col.find().count() == len(symbols):
        logger.info("SYMBOLS are already existed and no more to update")
    else:
        logger.info("Delete the original symbols collections")
        db_cli.bitmex.drop_collection("symbols")
        logger.info("Downloading the new symbols")
        col.insert_many(symbols)
        logger.info("Symbols download is done! Thank you man!")


def save_symbols_json(active: bool, dst_path: str):
    symbols = fetch_bitmex_symbols(active)
    with open(dst_path, 'w') as f:
        json.dumps(symbols, f)
