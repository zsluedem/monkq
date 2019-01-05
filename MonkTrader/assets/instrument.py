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
import dataclasses
import datetime
from dateutil.parser import parse

@dataclasses.dataclass()
class Instrument():
    symbol: str = None

    listing_date: datetime.datetime = None
    expiry_date: datetime.datetime = None

    underlying: str = None
    quote_currency: str = None

    lot_size: float = None
    tick_size: float = None

    maker_fee: float = None
    taker_fee: float = None

    @classmethod
    def create(cls, key_map:dict, values:dict):
        annotation_dict = {}
        for mro in cls.__mro__[::-1]:
            if mro is object:
                continue
            annotation_dict.update(mro.__annotations__)
        init_values = {}
        for k, v in values.items():
            annotate = annotation_dict.get(key_map.get(k))
            if annotate is None:
                continue
            elif annotate == datetime.datetime:
                if not isinstance(v, datetime.datetime):
                    v = parse(v)
            init_values.update({key_map.get(k): v})

        return cls(**init_values)

    @property
    def exchange(self)-> None:
        return

    @property
    def state(self):
        return

@dataclasses.dataclass()
class FutureInstrument(Instrument):
    root_symbol:str = None
    init_margin: float = 0
    main_margin: float = 0

    settlement_fee: float = 0
    settle_currency: str = None

    settle_date: datetime.datetime = None
    front_date: datetime.datetime = None

    reference_symbol: str = None

    deleverage: bool = True

@dataclasses.dataclass()
class UpsideInstrument(FutureInstrument):
    pass

@dataclasses.dataclass()
class DownsideInstrument(FutureInstrument):
    pass

@dataclasses.dataclass()
class PerpetualInstrument(FutureInstrument):
    @property
    def funding_rate(self) -> float:
        return 0