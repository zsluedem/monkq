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
import requests
import json


def cal_liq_price(open_price: float, current_position: int, leverage: float, buy_amount: int, long: bool):
    pass


def cal_liq_price_isolate():
    pass


def get_recent_klines(symbol: str, frequency: str, count: int):
    query = {
        "symbol": symbol,
        "binSize": frequency,
        "count": count,
        "reverse": "true"
    }
    resp = requests.get("https://www.bitmex.com/api/v1/" + "trade/bucketed", params=query,
                        proxies={'https': "http://127.0.0.1:1087"})
    content = resp.content
    return json.loads(content)


if __name__ == '__main__':
    print(get_recent_klines('XBTUSD', '1m', 500))
