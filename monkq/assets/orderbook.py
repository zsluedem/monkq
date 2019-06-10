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
from dataclasses import dataclass
from typing import Any, Dict, List

from monkq.assets.const import SIDE


@dataclass
class BookItem():
    side: SIDE
    size: float
    price: float
    raw: Any


class AbcOrderBookStruct:
    def delete(self, data: Any) -> None:
        raise NotImplementedError()

    def insert(self, data: Any) -> None:
        raise NotImplementedError()

    def update(self, data: Any) -> None:
        raise NotImplementedError()

    def best_bid(self) -> BookItem:
        raise NotImplementedError()

    def best_ask(self) -> BookItem:
        raise NotImplementedError()

    def best_bid_n(self, n: int) -> List[BookItem]:
        raise NotImplementedError()

    def best_ask_n(self, n: int) -> List[BookItem]:
        raise NotImplementedError()


class DictStructOrderBook(AbcOrderBookStruct):
    def __init__(self) -> None:
        self._ask_book: Dict[int, BookItem] = {}
        self._bid_book: Dict[int, BookItem] = {}

        self._partial = False

    def delete(self, data: Dict) -> None:
        side = data.get('side')
        if side == 'Buy':
            self._bid_book.pop(data['id'])
        elif side == "Sell":
            self._ask_book.pop(data['id'])
        else:
            raise NotImplementedError()

    def insert(self, data: Dict) -> None:
        side = data.get('side')
        raw = data.get('raw') or data
        if side == 'Buy':
            book_item = BookItem(side=SIDE.BUY, size=data['size'], price=data['price'], raw=raw)
            self._bid_book[data['id']] = book_item
        elif side == "Sell":
            book_item = BookItem(side=SIDE.SELL, size=data['size'], price=data['price'], raw=raw)
            self._ask_book[data['id']] = book_item
        else:
            raise NotImplementedError()

    def update(self, data: Dict) -> None:
        side = data.get('side')
        raw = data.get('raw') or data
        if side == 'Buy':
            book_item = self._bid_book.get(data['id'])
            if book_item is not None:
                book_item.size = data['size']
                book_item.raw = raw
            else:
                self.insert(data)
        elif side == "Sell":
            book_item = self._ask_book.get(data['id'])
            if book_item is not None:
                book_item.size = data['size']
                book_item.raw = raw
            else:
                self.insert(data)
        else:
            raise NotImplementedError()

    def best_bid(self) -> BookItem:
        return max(self._bid_book.values(), key=lambda x: x.price)

    def best_ask(self) -> BookItem:
        return min(self._ask_book.values(), key=lambda x: x.price)

    def best_bid_n(self, n: int) -> List[BookItem]:
        return sorted(self._bid_book.values(), key=lambda x: x.price, reverse=True)[:n]

    def best_ask_n(self, n: int) -> List[BookItem]:
        return sorted(self._ask_book.values(), key=lambda x: x.price)[:n]
