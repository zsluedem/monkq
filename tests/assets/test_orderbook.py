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
from monkq.assets.orderbook import DictStructOrderBook


def test_dictorderbook() -> None:
    init_data = [{'symbol': 'XBTUSD', 'id': 15599138250, 'side': 'Sell', 'size': 306, 'price': 8617.5},
                 {'symbol': 'XBTUSD', 'id': 15599138500, 'side': 'Sell', 'size': 50, 'price': 8615},
                 {'symbol': 'XBTUSD', 'id': 15599138550, 'side': 'Sell', 'size': 500, 'price': 8614.5},
                 {'symbol': 'XBTUSD', 'id': 15599138650, 'side': 'Sell', 'size': 199, 'price': 8613.5},
                 {'symbol': 'XBTUSD', 'id': 15599138700, 'side': 'Sell', 'size': 50, 'price': 8613},
                 {'symbol': 'XBTUSD', 'id': 15599138750, 'side': 'Sell', 'size': 126, 'price': 8612.5},
                 {'symbol': 'XBTUSD', 'id': 15599138800, 'side': 'Sell', 'size': 144, 'price': 8612},
                 {'symbol': 'XBTUSD', 'id': 15599138900, 'side': 'Sell', 'size': 781, 'price': 8611},
                 {'symbol': 'XBTUSD', 'id': 15599138950, 'side': 'Sell', 'size': 36, 'price': 8610.5},
                 {'symbol': 'XBTUSD', 'id': 15599139000, 'side': 'Sell', 'size': 72, 'price': 8610},
                 {'symbol': 'XBTUSD', 'id': 15599139250, 'side': 'Sell', 'size': 133, 'price': 8607.5},
                 {'symbol': 'XBTUSD', 'id': 15599139300, 'side': 'Sell', 'size': 1126, 'price': 8607},
                 {'symbol': 'XBTUSD', 'id': 15599139350, 'side': 'Sell', 'size': 125, 'price': 8606.5},
                 {'symbol': 'XBTUSD', 'id': 15599139400, 'side': 'Sell', 'size': 326, 'price': 8606},
                 {'symbol': 'XBTUSD', 'id': 15599139500, 'side': 'Sell', 'size': 197, 'price': 8605},
                 {'symbol': 'XBTUSD', 'id': 15599139550, 'side': 'Sell', 'size': 1050, 'price': 8604.5},
                 {'symbol': 'XBTUSD', 'id': 15599139600, 'side': 'Sell', 'size': 51, 'price': 8604},
                 {'symbol': 'XBTUSD', 'id': 15599139650, 'side': 'Sell', 'size': 25, 'price': 8603.5},
                 {'symbol': 'XBTUSD', 'id': 15599139700, 'side': 'Sell', 'size': 25, 'price': 8603},
                 {'symbol': 'XBTUSD', 'id': 15599139750, 'side': 'Sell', 'size': 104, 'price': 8602.5},
                 {'symbol': 'XBTUSD', 'id': 15599139800, 'side': 'Sell', 'size': 273, 'price': 8602},
                 {'symbol': 'XBTUSD', 'id': 15599139850, 'side': 'Sell', 'size': 125, 'price': 8601.5},
                 {'symbol': 'XBTUSD', 'id': 15599139900, 'side': 'Sell', 'size': 17788, 'price': 8601},
                 {'symbol': 'XBTUSD', 'id': 15599139950, 'side': 'Sell', 'size': 2227383, 'price': 8600.5},
                 {'symbol': 'XBTUSD', 'id': 15599140000, 'side': 'Sell', 'size': 31352, 'price': 8600},
                 {'symbol': 'XBTUSD', 'id': 15599140100, 'side': 'Buy', 'size': 194033, 'price': 8599},
                 {'symbol': 'XBTUSD', 'id': 15599140200, 'side': 'Buy', 'size': 70, 'price': 8598},
                 {'symbol': 'XBTUSD', 'id': 15599140250, 'side': 'Buy', 'size': 3088, 'price': 8597.5},
                 {'symbol': 'XBTUSD', 'id': 15599140300, 'side': 'Buy', 'size': 121, 'price': 8597},
                 {'symbol': 'XBTUSD', 'id': 15599140350, 'side': 'Buy', 'size': 95, 'price': 8596.5},
                 {'symbol': 'XBTUSD', 'id': 15599140400, 'side': 'Buy', 'size': 595, 'price': 8596},
                 {'symbol': 'XBTUSD', 'id': 15599140450, 'side': 'Buy', 'size': 25, 'price': 8595.5},
                 {'symbol': 'XBTUSD', 'id': 15599140500, 'side': 'Buy', 'size': 25, 'price': 8595},
                 {'symbol': 'XBTUSD', 'id': 15599140600, 'side': 'Buy', 'size': 50, 'price': 8594},
                 {'symbol': 'XBTUSD', 'id': 15599140650, 'side': 'Buy', 'size': 511, 'price': 8593.5},
                 {'symbol': 'XBTUSD', 'id': 15599140800, 'side': 'Buy', 'size': 500, 'price': 8592},
                 {'symbol': 'XBTUSD', 'id': 15599141000, 'side': 'Buy', 'size': 500, 'price': 8590},
                 {'symbol': 'XBTUSD', 'id': 15599141500, 'side': 'Buy', 'size': 134, 'price': 8585},
                 {'symbol': 'XBTUSD', 'id': 15599141600, 'side': 'Buy', 'size': 40, 'price': 8584},
                 {'symbol': 'XBTUSD', 'id': 15599142000, 'side': 'Buy', 'size': 6, 'price': 8580},
                 {'symbol': 'XBTUSD', 'id': 15599142050, 'side': 'Buy', 'size': 20, 'price': 8579.5},
                 {'symbol': 'XBTUSD', 'id': 15599142150, 'side': 'Buy', 'size': 125, 'price': 8578.5},
                 {'symbol': 'XBTUSD', 'id': 15599142200, 'side': 'Buy', 'size': 52, 'price': 8578},
                 {'symbol': 'XBTUSD', 'id': 15599142300, 'side': 'Buy', 'size': 1366, 'price': 8577},
                 {'symbol': 'XBTUSD', 'id': 15599142400, 'side': 'Buy', 'size': 504, 'price': 8576},
                 {'symbol': 'XBTUSD', 'id': 15599142500, 'side': 'Buy', 'size': 250, 'price': 8575},
                 {'symbol': 'XBTUSD', 'id': 15599142600, 'side': 'Buy', 'size': 500, 'price': 8574},
                 {'symbol': 'XBTUSD', 'id': 15599142700, 'side': 'Buy', 'size': 500, 'price': 8573},
                 {'symbol': 'XBTUSD', 'id': 15599142800, 'side': 'Buy', 'size': 500, 'price': 8572},
                 {'symbol': 'XBTUSD', 'id': 15599142900, 'side': 'Buy', 'size': 154, 'price': 8571}]

    order_book = DictStructOrderBook()
    for data in init_data:
        order_book.insert(data)
    assert order_book.best_bid().price == 8599
    assert order_book.best_bid().size == 194033
    assert order_book.best_ask().price == 8600
    assert order_book.best_ask().size == 31352

    assert len(order_book.best_bid_n(3)) == 3
    assert len(order_book.best_ask_n(4)) == 4

    assert order_book.best_bid_n(3)[2].price == 8597.5
    assert order_book.best_bid_n(3)[2].size == 3088

    assert order_book.best_ask_n(3)[2].price == 8601
    assert order_book.best_ask_n(3)[2].size == 17788

    order_book.delete({'symbol': 'XBTUSD', 'id': 15599140800, 'side': 'Buy'})
    order_book.delete({'symbol': 'XBTUSD', 'id': 15599141000, 'side': 'Buy'})

    assert order_book.best_bid_n(11)[10].price == 8585
    assert order_book.best_bid_n(11)[10].size == 134
    order_book.insert({'symbol': 'XBTUSD', 'id': 15599140700, 'side': 'Buy', 'size': 500, 'price': 8593})
    order_book.insert({'symbol': 'XBTUSD', 'id': 15599140900, 'side': 'Buy', 'size': 500, 'price': 8591})

    assert order_book.best_bid_n(11)[10].price == 8593
    assert order_book.best_bid_n(11)[10].size == 500
    order_book.update({"symbol": "XBTUSD", "id": 15599140400, "side": "Buy", "size": 195})
    assert order_book.best_bid_n(6)[5].price == 8596
    assert order_book.best_bid_n(6)[5].size == 195

    order_book.delete({'symbol': 'XBTUSD', 'id': 15599140000, 'side': 'Sell'})

    assert order_book.best_ask().price == 8600.5
    assert order_book.best_ask().size == 2227383
    order_book.insert({'symbol': 'XBTUSD', 'id': 15599141800, 'side': 'Sell', 'size': 500, 'price': 8599.5})

    assert order_book.best_ask().price == 8599.5
    assert order_book.best_ask().size == 500

    order_book.update({"symbol": "XBTUSD", "id": 15599141800, "side": "Sell", "size": 195})
    assert order_book.best_ask().price == 8599.5
    assert order_book.best_ask().size == 195
