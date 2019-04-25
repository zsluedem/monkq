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
from urllib.parse import urljoin

from monkq.utils.timefunc import utc_datetime

TRADE_LINK = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/{}.csv.gz"
QUOTE_LINK = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/quote/{}.csv.gz"
BITMEX_API_URL = "https://www.bitmex.com/api/v1/"
BITMEX_WEBSOCKET_URL = "wss://www.bitmex.com/realtime"
BITMEX_TESTNET_API_URL = "https://testnet.bitmex.com/api/v1/"
BITMEX_TESTNET_WEBSOCKET_URL = "wss://testnet.bitmex.com/realtime"
SYMBOL_LINK = urljoin(BITMEX_API_URL, "instrument?count=500")
TARFILETYPE = '.csv.gz'
INSTRUMENT_FILENAME = 'instruments.json'
START_DATE = utc_datetime(2014, 11, 22)  # bitmex open date

TRADE_FILE_NAME = 'trade.hdf'
QUOTE_FILE_NAME = 'quote.hdf'
KLINE_FILE_NAME = 'kline.hdf'
