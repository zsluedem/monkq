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
from MonkTrader.exchange.base import BaseExchange

T_INSTRUMENT = TypeVar('T_INSTRUMENT', bound="Instrument")


@dataclasses.dataclass(frozen=True)
class Instrument():
    exchange: BaseExchange
    symbol: str

    listing_date: Optional[datetime.datetime] = None
    expiry_date: Optional[datetime.datetime] = None

    underlying: Optional[str] = None
    quote_currency: Optional[str] = None

    lot_size: Optional[float] = None
    tick_size: Optional[float] = None

    maker_fee: float = 0
    taker_fee: float = 0

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
        return self.exchange.get_last_price(self)  # type:ignore


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


@dataclasses.dataclass(frozen=True)
class UpsideInstrument(FutureInstrument):
    pass


@dataclasses.dataclass(frozen=True)
class DownsideInstrument(FutureInstrument):
    pass


@dataclasses.dataclass(frozen=True)
class PerpetualInstrument(FutureInstrument):
    @property
    def funding_rate(self) -> float:
        return 0
