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
import os
from typing import Dict, Iterator, List, Optional, Tuple

import pandas
from dateutil.relativedelta import relativedelta
from logbook import Logger
from monkq.config.global_settings import (
    HDF_FILE_COMPRESS_LEVEL, HDF_FILE_COMPRESS_LIB,
    HDF_TRADE_TO_KLINE_CHUNK_SIZE,
)
from monkq.data import DataProcessor, Point, ProcessPoints
from monkq.exception import DataDownloadError
from monkq.exchange.bitmex.const import (
    INSTRUMENT_FILENAME, KLINE_FILE_NAME, START_DATE, TRADE_FILE_NAME,
)
from monkq.utils.i18n import _
from monkq.utils.timefunc import parse_datetime_str, utc_datetime

from ..log import logger_group
from .utils import (
    check_1m_data_integrity, fullfill_1m_kline_with_start_end,
    trades_to_1m_kline,
)

logger = Logger('exchange.bitmex.data')
logger_group.add_logger(logger)


class KlinePoint(Point):
    __slots__ = ('df', 'key')

    def __init__(self, df: Optional[pandas.DataFrame], key: str) -> None:
        self.df = df  # if df is None, then it is an end point
        self.key = key

    @property
    def value(self) -> pandas.DataFrame:
        return self.df


class BitMexKlineProcessPoints(ProcessPoints):
    def __init__(self, input_file: str, output_file: str) -> None:
        self.input_file = input_file
        self.output_file = output_file

    def __iter__(self) -> Iterator[KlinePoint]:
        try:
            trade_hdf = pandas.HDFStore(self.input_file, 'r')
        except OSError:  # not exist
            raise DataDownloadError(_("The required trade.hdf doesn't exist. Download the kline data of Bitmex need "
                                      "the Bitmex trade data.You have to download the trade data first."
                                      "Run 'monktrader download --kind trade'"))
        keys = trade_hdf.keys()
        trade_hdf.close()

        for key in keys:
            if os.path.exists(self.output_file):
                logger.info(_("Updating new kline data from new trade data."))
                try:
                    kline_hdf = pandas.HDFStore(self.output_file, 'r')
                    last = kline_hdf.select_column(key, 'index', start=-1)
                    last_time = last[0]
                    start_time = last_time + relativedelta(days=1)
                except KeyError:  # not exist
                    start_time = START_DATE
                finally:
                    kline_hdf.close()
            else:
                logger.info(_("You don't have any kline data. We are going to "
                              "generate the kline data from scratch"))
                start_time = START_DATE

            logger.info(_("Generating kline data {} now from date {}.").format(key, start_time))
            found = False
            iter_df = pandas.read_hdf(self.input_file, key,
                                      where="index>=datetime.datetime({},{},{})".format(start_time.year,
                                                                                        start_time.month,
                                                                                        start_time.day),
                                      columns=['price', 'homeNotional', 'foreignNotional'],
                                      chunksize=HDF_TRADE_TO_KLINE_CHUNK_SIZE, iterator=True)
            for df in iter_df:
                yield KlinePoint(df, key)
                found = True
            else:
                if found:
                    # finally yield an end point to process the cache last date
                    yield KlinePoint(None, key)
                    logger.info(_("Successfully generate kline data "
                                  "{}").format(key))


class BitMexKlineTransform(DataProcessor):
    def __init__(self, input_dir: str, output_dir: str) -> None:
        self.input_file = os.path.join(input_dir, TRADE_FILE_NAME)
        self.output_file = os.path.join(output_dir, KLINE_FILE_NAME)

        self.mark_point = START_DATE
        self.cache = None

    def process_points(self) -> BitMexKlineProcessPoints:
        return BitMexKlineProcessPoints(self.input_file, self.output_file)

    def process_one_point(self, point: KlinePoint) -> None:
        # if df is None, it is an end point
        if point.df is None:
            if self.cache is not None:
                kline = trades_to_1m_kline(self.cache)
                kline.to_hdf(self.output_file, point.key, mode='a',
                             format='table', data_columns=True, index=False,
                             complib=HDF_FILE_COMPRESS_LIB, complevel=HDF_FILE_COMPRESS_LEVEL, append=True)
                logger.debug("Finished data {}".format(point.key))
                # reset everything for another key
                self.cache = None
                self.mark_point = START_DATE
            return

        end_time = point.df.index[-1]
        last_date = end_time + relativedelta(hour=0, minute=0, second=0, microsecond=0)
        logger.debug("Process {} data from {} to {}".format(point.key, self.mark_point, last_date))
        if last_date > self.mark_point:
            process_df = point.df.loc[
                point.df.index < utc_datetime(last_date.year, last_date.month, last_date.day)]
            cache_df = point.df.loc[point.df.index >= utc_datetime(last_date.year, last_date.month, last_date.day)]

            if self.cache is not None:
                process_df = pandas.concat([self.cache, process_df], copy=False)

            if len(process_df) != 0:
                kline = trades_to_1m_kline(process_df)
                logger.debug("Write {} data from {} to {} into hdf file"
                             .format(point.key, self.mark_point, last_date))
                kline.to_hdf(self.output_file, point.key, mode='a',
                             format='table', data_columns=True, index=False,
                             complib=HDF_FILE_COMPRESS_LIB, complevel=HDF_FILE_COMPRESS_LEVEL, append=True)

            self.cache = cache_df
            self.mark_point = last_date
        else:
            if self.cache is None:
                self.cache = point.df
            else:
                self.cache = pandas.concat([self.cache, point.df], copy=False)

    def last(self) -> None:
        pass


class FullFillPoint(Point):
    def __init__(self, df: pandas.DataFrame, instruemt_data: dict, key: str):
        self.df = df
        self.instrument_data = instruemt_data
        self.key = key

    @property
    def value(self) -> pandas.DataFrame:
        return self.df


class KlineFullFileProcessPoints(ProcessPoints):
    def __init__(self, instrument_data: Dict[str, dict], kline_hdf_path: str) -> None:
        self.kline_hdf_path = kline_hdf_path
        self.instrument_data = instrument_data

        self.keys = self.get_keys()

    def __iter__(self) -> Iterator[FullFillPoint]:
        for key in self.keys:
            df = pandas.read_hdf(self.kline_hdf_path, key)
            yield FullFillPoint(df, self.instrument_data[key], key)

    def get_keys(self) -> List[str]:
        kline = pandas.HDFStore(self.kline_hdf_path)
        kline_keys = kline.keys()
        kline.close()
        kline_keys = [key.strip('/') for key in kline_keys]
        return kline_keys


class KlineFullFill(DataProcessor):
    def __init__(self, input_dir: str) -> None:
        with open(os.path.join(input_dir, INSTRUMENT_FILENAME)) as f:
            instrument_data: List[dict] = json.load(f)
        self.instrument_data = self.reformat_instrument_data(instrument_data)
        self.output_file = os.path.join(input_dir, KLINE_FILE_NAME)

    def reformat_instrument_data(self, data: List[dict]) -> Dict[str, dict]:
        outcome = {}
        for instrument in data:
            outcome[instrument['symbol']] = instrument
        return outcome

    def process_points(self) -> KlineFullFileProcessPoints:
        return KlineFullFileProcessPoints(self.instrument_data, self.output_file)

    def process_one_point(self, point: FullFillPoint) -> None:
        logger.debug("Full fill kline data {}.".format(point.key))
        df = point.value
        list_datetime, last_datetime = self.get_start_end(point.key, df)

        logger.debug("Kline data start point is: {}, end point is: {}.".format(list_datetime, last_datetime))

        if check_1m_data_integrity(df, list_datetime, last_datetime):
            logger.debug("Check kline is complete, doesn't have to full fill.")
        else:
            logger.debug("Kline data is not full fill, try to full fill.")
            fullfill_df = fullfill_1m_kline_with_start_end(df, list_datetime, last_datetime)

            fullfill_df.to_hdf(self.output_file, key=point.key, mode='a',
                               format='fixed', data_columns=True,
                               index=False, complib=HDF_FILE_COMPRESS_LIB,
                               complevel=HDF_FILE_COMPRESS_LEVEL)

    def get_start_end(self, key: str, df: pandas.DataFrame) -> Tuple[datetime.datetime, datetime.datetime]:
        instrument = self.instrument_data[key]
        list_datetime = parse_datetime_str(instrument['listing'])
        start = list_datetime + relativedelta(minutes=1)

        last_pd_datetime = df.index[-1]
        last_pd_datetime = last_pd_datetime.to_pydatetime()
        if instrument.get('expiry'):
            expiry_datetime = parse_datetime_str(instrument['expiry'])
            if expiry_datetime > last_pd_datetime:
                logger.debug("Instrument {} haven't expired yet. "
                             "Expiry date: {}, last_kline_date: {}.".format(key, expiry_datetime, last_pd_datetime))
                last_datetime = last_pd_datetime + relativedelta(days=+1, hour=0, minute=0, second=0, microsecond=0)
            else:
                logger.debug("Instrument {} has expired. Use expiry date {}".format(key, expiry_datetime))
                last_datetime = expiry_datetime
        else:
            logger.debug("Instrument {} doesn't have expiry date."
                         "Use the df last datetime as the last date."
                         "Original kline last datetime is {}".format(key, last_pd_datetime))

            last_datetime = last_pd_datetime + relativedelta(days=+1, hour=0, minute=0, second=0, microsecond=0)
        return (start, last_datetime)

    def last(self) -> None:
        pass
