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
import dataclasses
import datetime
from typing import Optional, Type, TypeVar

from dateutil.parser import parse
from monkq.exchange.base import BaseExchange, BaseSimExchange

T_INSTRUMENT = TypeVar('T_INSTRUMENT', bound="Instrument")


@dataclasses.dataclass(frozen=True)
class Instrument():
    exchange: BaseSimExchange
    symbol: str

    listing_date: Optional[datetime.datetime] = None
    expiry_date: Optional[datetime.datetime] = None

    underlying: Optional[str] = None
    quote_currency: Optional[str] = None

    lot_size: Optional[float] = None
    tick_size: Optional[float] = None

    maker_fee: float = 0
    taker_fee: float = 0

    def __getstate__(self) -> dict:
        return {
            'exchange': self.exchange.name,
            'symbol': self.symbol,
            'listing_date': self.listing_date,
            'expiry_date': self.expiry_date,
            'underlying': self.underlying,
            'quote_currency': self.quote_currency,
            'lot_size': self.lot_size,
            'tick_size': self.tick_size,
            'maker_fee': self.maker_fee,
            'taker_fee': self.taker_fee
        }

    @classmethod
    def create(cls: Type[T_INSTRUMENT], key_map: dict, values: dict, exchange: BaseExchange) -> T_INSTRUMENT:
        annotation_dict = {}
        for mro in cls.__mro__[::-1]:
            if mro is object:
                continue
            annotation_dict.update(mro.__annotations__)
        init_values = {}
        for k, v in values.items():
            key_map_value = key_map.get(k)
            if key_map_value is None:
                continue
            annotate = annotation_dict.get(key_map_value)
            if annotate is None:
                continue
            elif annotate == Optional[datetime.datetime]:
                if not isinstance(v, datetime.datetime):
                    v = parse(v) if v is not None else v
            init_values.update({key_map.get(k): v})
        init_values.update({'exchange': exchange})
        return cls(**init_values)  # type: ignore

    @property
    def state(self) -> None:
        return

    @property
    def last_price(self) -> float:
        return self.exchange.last_price(self)


@dataclasses.dataclass(frozen=True)
class FutureInstrument(Instrument):
    root_symbol: Optional[str] = None
    init_margin_rate: float = 0
    maint_margin_rate: float = 0

    settlement_fee: float = 0
    settle_currency: Optional[str] = None

    settle_date: Optional[datetime.datetime] = None
    front_date: Optional[datetime.datetime] = None

    reference_symbol: Optional[str] = None

    deleverage: bool = True

    def __getstate__(self) -> dict:
        state = super(FutureInstrument, self).__getstate__()
        state.update({
            'root_symbol': self.root_symbol,
            'init_margin_rate': self.init_margin_rate,
            'maint_margin_rate': self.maint_margin_rate,
            'settlement_fee': self.settlement_fee,
            'settle_currency': self.settle_currency,
            'settle_date': self.settle_date,
            'front_date': self.front_date,
            'reference_symbol': self.reference_symbol,
            'deleverage': self.deleverage
        })
        return state


@dataclasses.dataclass(frozen=True)
class CallOptionInstrument(FutureInstrument):
    pass


@dataclasses.dataclass(frozen=True)
class PutOptionInstrument(FutureInstrument):
    pass


@dataclasses.dataclass(frozen=True)
class PerpetualInstrument(FutureInstrument):
    @property
    def funding_rate(self) -> float:
        return 0


@dataclasses.dataclass(frozen=True)
class AbandonInstrument(Instrument):
    pass
