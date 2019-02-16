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
import os
from typing import TYPE_CHECKING, Dict, Type

from MonkTrader.assets.instrument import (
    DownsideInstrument, FutureInstrument, Instrument, PerpetualInstrument,
    UpsideInstrument,
)
from MonkTrader.data import DataLoader
from MonkTrader.exception import LoadDataError
from MonkTrader.exchange.bitmex.const import INSTRUMENT_FILENAME, TRADES_DATA_F

from .utils import read_trade_tar

if TYPE_CHECKING:
    from MonkTrader.exchange.bitmex.exchange import BitmexSimulateExchange

instrument_map = {
    'symbol': 'symbol',
    "rootSymbol": 'root_symbol',
    'listing': 'listing_date',
    'expiry': 'expiry_date',
    'underlying': 'underlying',
    "quoteCurrency": 'quote_currency',
    'lotSize': 'lot_size',
    'tickSize': 'tick_size',
    'makerFee': 'maker_fee',
    'takerFee': 'taker_fee',

    'initMargin': 'init_margin_rate',
    'maintMargin': 'maint_margin_rate',

    'settlementFee': 'settlement_fee',
    'settlCurrency': 'settle_currency',

    'settle': 'settle_date',
    'front': 'front_date',
    'referenceSymbol': 'reference_symbol',
    'deleverage': 'deleverage'
}


class BitmexDataloader(DataLoader):
    instrument_cls: Dict[str, Type[Instrument]] = {
        'OPECCS': DownsideInstrument,  # put options
        'OCECCS': UpsideInstrument,  # call options
        'FFCCSX': FutureInstrument,  # normal futures contracts
        'FFWCSX': PerpetualInstrument,  # perpetual  futures contracts
    }

    def __init__(self, exchange: 'BitmexSimulateExchange', data_dir: str) -> None:
        self.data_dir = data_dir
        self.instruments: Dict[str, Instrument] = dict()
        self.exchange = exchange
        self.trade_data = dict()

    def load_instruments(self) -> None:
        instruments_file = os.path.join(self.data_dir, INSTRUMENT_FILENAME)
        with open(instruments_file) as f:
            instruments_raw = json.load(f)
        for instrument_raw in instruments_raw:
            instrument_cls = self.instrument_cls.get(instrument_raw['typ'])
            if instrument_cls is None:
                raise LoadDataError()
            instrument = instrument_cls.create(instrument_map, instrument_raw, self.exchange)
            self.instruments[instrument.symbol] = instrument

    def load_trades(self) -> None:
        base = os.path.join(self.data_dir, TRADES_DATA_F)
        directories = os.listdir(base)
        directories.sort()
        for directory in directories:
            date_file = os.path.join(base, directory)
            symbols_files = os.listdir(date_file)
            for path in symbols_files:
                symbol = path.split('.')[0]
                data = read_trade_tar(os.path.join(date_file, path), False, False)
                if self.trade_data.get(symbol) is None:
                    self.trade_data[symbol] = data
                else:
                    self.trade_data[symbol] = self.trade_data[symbol].append(data, ignore_index=True)

    def resample_trades(self, freq: str) -> None:
        pass


if __name__ == '__main__':
    b = BitmexDataloader('s', 's')
