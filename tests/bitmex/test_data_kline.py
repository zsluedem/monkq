import os
import tempfile
import json
import random
import datetime
import numpy as np
from unittest.mock import patch

import pandas
from MonkTrader.exchange.bitmex.const import TRADE_FILE_NAME, INSTRUMENT_FILENAME, KLINE_FILE_NAME
from MonkTrader.exchange.bitmex.data.kline import BitMexKlineTransform, KlineFullFill
from MonkTrader.exchange.bitmex.data.utils import (
    check_1m_data_integrity, fullfill_1m_kline_with_start_end,
    trades_to_1m_kline,
)
from MonkTrader.utils import utc_datetime

from .conftest import random_kline_data, random_trade_frame, random_kline_data_with_start_end


def compare_dataframe_time(df1: pandas.DataFrame, df2: pandas.DataFrame, time: datetime.datetime) -> None:
    s1 = df1.loc[time]
    s2 = df2.loc[time]
    assert s1['close'] == s2['close']
    assert s1['open'] == s2['open']
    assert s1['high'] == s2['high']
    assert s1['low'] == s2['low']
    assert s1['volume'] == s2['volume']
    assert s1['turnover'] == s2['turnover']


def compare_dataframe_filled(df1: pandas.DataFrame, time1: datetime.datetime,
                             df2: pandas.DataFrame, time2: datetime.datetime) -> None:
    s1 = df1.loc[time1]
    s2 = df2.loc[time2]
    assert s1['close'] == s2['close']
    assert s1['open'] == s2['open']
    assert s1['high'] == s2['high']
    assert s1['low'] == s2['low']
    assert s1['volume'] == 0
    assert s1['turnover'] == 0


def compare_datafrome_index(df1: pandas.DataFrame, df2: pandas.DataFrame, index: int) -> None:
    assert df1.index[index] == df2.index[index]
    assert df1['close'][index] == df2['close'][index]
    assert df1['open'][index] == df2['open'][index]
    assert df1['high'][index] == df2['high'][index]
    assert df1['low'][index] == df2['low'][index]
    assert df1['volume'][index] == df2['volume'][index]
    assert df1['turnover'][index] == df2['turnover'][index]


def asset_df_nan(df: pandas.DataFrame, index: int) -> None:
    assert np.isnan(df['close'][index])
    assert np.isnan(df['open'][index])
    assert np.isnan(df['high'][index])
    assert np.isnan(df['low'][index])
    assert df['volume'][index] == 0
    assert df['turnover'][index] == 0


def write_hdf(df: pandas.DataFrame, path: str, key: str) -> None:
    df.to_hdf(path, key, mode='a',
              format='table', data_columns=True,
              complib='blosc', complevel=9, append=True)


def test_trade_to_1m_kline() -> None:
    df1 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 0, 1))
    df2 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 0, 1))
    df3 = random_trade_frame(10, utc_datetime(2018, 1, 4, 12, 0, 1))

    frame = df1.append(df2).append(df3)

    outcome = trades_to_1m_kline(frame)

    assert len(outcome) == 4321

    assert outcome['high'][0] == max(df1['price'])
    assert outcome['low'][0] == min(df1['price'])
    assert outcome['open'][0] == df1['price'][0]
    assert outcome['close'][0] == df1['price'][-1]
    assert outcome['volume'][0] == sum(df1['homeNotional'])
    assert outcome['turnover'][0] == sum(df1['foreignNotional'])

    assert outcome['high'][20] == max(df1['price'])
    assert outcome['low'][20] == min(df1['price'])
    assert outcome['open'][20] == df1['price'][0]
    assert outcome['close'][20] == df1['price'][-1]
    assert outcome['volume'][20] == 0
    assert outcome['turnover'][20] == 0

    assert outcome['high'][-1] == max(df3['price'])
    assert outcome['low'][-1] == min(df3['price'])
    assert outcome['open'][-1] == df3['price'][0]
    assert outcome['close'][-1] == df3['price'][-1]
    assert outcome['volume'][-1] == sum(df3['homeNotional'])
    assert outcome['turnover'][-1] == sum(df3['foreignNotional'])


def test_check_1m_data_integrity() -> None:
    df1 = random_kline_data(10, utc_datetime(2018, 1, 1, 12, 10))

    assert check_1m_data_integrity(df1, utc_datetime(2018, 1, 1, 12), utc_datetime(2018, 1, 1, 12, 10))
    assert not check_1m_data_integrity(df1, utc_datetime(2018, 1, 1, 12, 1),
                                       utc_datetime(2018, 1, 1, 12, 10))

    assert not check_1m_data_integrity(df1, utc_datetime(2018, 1, 1, 12), utc_datetime(2018, 1, 1, 12, 12))


def test_fullfill_kline_func() -> None:
    k_df1 = random_kline_data(1000, utc_datetime(2018, 1, 2, 12, 30))
    k_df2 = random_kline_data(1000, utc_datetime(2018, 1, 6, 12, 30))

    kline_df = k_df1.append(k_df2)

    full_kline = fullfill_1m_kline_with_start_end(kline_df,
                                                  utc_datetime(2018, 1, 1, 12, 1),
                                                  utc_datetime(2018, 1, 20, 12))

    assert len(full_kline) == 27360

    compare_dataframe_time(full_kline, k_df1, utc_datetime(2018, 1, 2, 12, 29))
    compare_dataframe_filled(full_kline, utc_datetime(2018, 1, 2, 12, 35), k_df1, utc_datetime(2018, 1, 2, 12, 30))

    compare_dataframe_time(full_kline, k_df2, utc_datetime(2018, 1, 6, 12, 25))
    compare_dataframe_filled(full_kline, utc_datetime(2018, 1, 6, 12, 35), k_df2, utc_datetime(2018, 1, 6, 12, 30))


def test_BitMexKlineTransform_from_scratch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, TRADE_FILE_NAME)

        df1 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 0, 1))
        df2 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 1, 1))
        df3 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 2, 1))
        hdf1 = df1.append(df2).append(df3)

        write_hdf(hdf1, target, "XBTUSD")

        df4 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 0, 1))
        df5 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 1, 1))
        df6 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 2, 1))

        df7 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 0, 1))
        df8 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 1, 1))
        df9 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 2, 1))

        df10 = random_trade_frame(10, utc_datetime(2018, 1, 5, 12, 2, 1))

        hdf2 = df4.append(df5).append(df6).append(df7).append(df8).append(df9).append(df10)

        write_hdf(hdf2, target, "TRXH19")

        with patch("MonkTrader.exchange.bitmex.data.kline.HDF_TRADE_TO_KLINE_CHUNK_SIZE", 5):
            b = BitMexKlineTransform(tmp, tmp)
            b.do_all()

        with pandas.HDFStore(os.path.join(tmp, 'kline.hdf')) as store:
            XBTUSD = store['XBTUSD']

            assert XBTUSD.index[0] == utc_datetime(2018, 1, 1, 12, 1)
            assert XBTUSD['high'][0] == max(df1['price'])
            assert XBTUSD['low'][0] == min(df1['price'])
            assert XBTUSD['open'][0] == df1['price'][0]
            assert XBTUSD['close'][0] == df1['price'][-1]
            assert XBTUSD['volume'][0] == sum(df1['homeNotional'])
            assert XBTUSD['turnover'][0] == sum(df1['foreignNotional'])

            assert XBTUSD.index[1] == utc_datetime(2018, 1, 1, 12, 2)
            assert XBTUSD['high'][1] == max(df2['price'])
            assert XBTUSD['low'][1] == min(df2['price'])
            assert XBTUSD['open'][1] == df2['price'][0]
            assert XBTUSD['close'][1] == df2['price'][-1]
            assert XBTUSD['volume'][1] == sum(df2['homeNotional'])
            assert XBTUSD['turnover'][1] == sum(df2['foreignNotional'])

            assert XBTUSD.index[2] == utc_datetime(2018, 1, 1, 12, 3)
            assert XBTUSD['high'][2] == max(df3['price'])
            assert XBTUSD['low'][2] == min(df3['price'])
            assert XBTUSD['open'][2] == df3['price'][0]
            assert XBTUSD['close'][2] == df3['price'][-1]
            assert XBTUSD['volume'][2] == sum(df3['homeNotional'])
            assert XBTUSD['turnover'][2] == sum(df3['foreignNotional'])

            TRXH19 = store['TRXH19']

            assert TRXH19.index[0] == utc_datetime(2018, 1, 1, 12, 1)
            assert TRXH19['high'][0] == max(df4['price'])
            assert TRXH19['low'][0] == min(df4['price'])
            assert TRXH19['open'][0] == df4['price'][0]
            assert TRXH19['close'][0] == df4['price'][-1]
            assert TRXH19['volume'][0] == sum(df4['homeNotional'])
            assert TRXH19['turnover'][0] == sum(df4['foreignNotional'])

            assert TRXH19.index[1] == utc_datetime(2018, 1, 1, 12, 2)
            assert TRXH19['high'][1] == max(df5['price'])
            assert TRXH19['low'][1] == min(df5['price'])
            assert TRXH19['open'][1] == df5['price'][0]
            assert TRXH19['close'][1] == df5['price'][-1]
            assert TRXH19['volume'][1] == sum(df5['homeNotional'])
            assert TRXH19['turnover'][1] == sum(df5['foreignNotional'])

            assert TRXH19.index[2] == utc_datetime(2018, 1, 1, 12, 3)
            assert TRXH19['high'][2] == max(df6['price'])
            assert TRXH19['low'][2] == min(df6['price'])
            assert TRXH19['open'][2] == df6['price'][0]
            assert TRXH19['close'][2] == df6['price'][-1]
            assert TRXH19['volume'][2] == sum(df6['homeNotional'])
            assert TRXH19['turnover'][2] == sum(df6['foreignNotional'])

            assert TRXH19.index[3] == utc_datetime(2018, 1, 2, 12, 1)
            assert TRXH19['high'][3] == max(df7['price'])
            assert TRXH19['low'][3] == min(df7['price'])
            assert TRXH19['open'][3] == df7['price'][0]
            assert TRXH19['close'][3] == df7['price'][-1]
            assert TRXH19['volume'][3] == sum(df7['homeNotional'])
            assert TRXH19['turnover'][3] == sum(df7['foreignNotional'])

            assert TRXH19.index[4] == utc_datetime(2018, 1, 2, 12, 2)
            assert TRXH19['high'][4] == max(df8['price'])
            assert TRXH19['low'][4] == min(df8['price'])
            assert TRXH19['open'][4] == df8['price'][0]
            assert TRXH19['close'][4] == df8['price'][-1]
            assert TRXH19['volume'][4] == sum(df8['homeNotional'])
            assert TRXH19['turnover'][4] == sum(df8['foreignNotional'])

            assert TRXH19.index[5] == utc_datetime(2018, 1, 2, 12, 3)
            assert TRXH19['high'][5] == max(df9['price'])
            assert TRXH19['low'][5] == min(df9['price'])
            assert TRXH19['open'][5] == df9['price'][0]
            assert TRXH19['close'][5] == df9['price'][-1]
            assert TRXH19['volume'][5] == sum(df9['homeNotional'])
            assert TRXH19['turnover'][5] == sum(df9['foreignNotional'])


def test_BitMexKlineTransform_with_data() -> None:
    with tempfile.TemporaryDirectory() as tmp_input:
        kline_hdf = os.path.join(tmp_input, 'kline.hdf')

        target = os.path.join(tmp_input, TRADE_FILE_NAME)
        kline_count = 10

        ori1 = random_trade_frame(10, utc_datetime(2018, 1, 1, 23, 50, 1))
        for i in range(kline_count - 1):
            ori1 = ori1.append(random_trade_frame(10, utc_datetime(2018, 1, 1, 23, 51 + i, 1)))
        df1 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 0, 1))
        df2 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 1, 1))
        df3 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 2, 1))

        hdf1 = ori1.append(df1).append(df2).append(df3)

        write_hdf(hdf1, target, "XBTUSD")

        ori2 = random_trade_frame(10, utc_datetime(2018, 1, 1, 23, 50, 1))
        for i in range(kline_count - 1):
            ori2 = ori2.append(random_trade_frame(10, utc_datetime(2018, 1, 1, 23, 51 + i, 1)))
        df4 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 0, 1))
        df5 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 1, 1))
        df6 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 2, 1))

        hdf2 = ori2.append(df4).append(df5).append(df6)

        write_hdf(hdf2, target, "TRXH19")

        kline_df1 = random_kline_data(kline_count, utc_datetime(2018, 1, 1, 23, 59))
        kline_df2 = random_kline_data(kline_count, utc_datetime(2018, 1, 1, 23, 59))

        write_hdf(kline_df1, kline_hdf, "XBTUSD")

        write_hdf(kline_df2, kline_hdf, 'TRXH19')

        b = BitMexKlineTransform(tmp_input, tmp_input)
        b.do_all()

        with pandas.HDFStore(kline_hdf) as store:
            XBTUSD = store['XBTUSD']
            assert len(XBTUSD) == 13
            assert XBTUSD.index[-3] == utc_datetime(2018, 1, 2, 12, 1)
            assert XBTUSD['high'][-3] == max(df1['price'])
            assert XBTUSD['low'][-3] == min(df1['price'])
            assert XBTUSD['open'][-3] == df1['price'][0]
            assert XBTUSD['close'][-3] == df1['price'][-1]
            assert XBTUSD['volume'][-3] == sum(df1['homeNotional'])
            assert XBTUSD['turnover'][-3] == sum(df1['foreignNotional'])

            assert XBTUSD.index[-2] == utc_datetime(2018, 1, 2, 12, 2)
            assert XBTUSD['high'][-2] == max(df2['price'])
            assert XBTUSD['low'][-2] == min(df2['price'])
            assert XBTUSD['open'][-2] == df2['price'][0]
            assert XBTUSD['close'][-2] == df2['price'][-1]
            assert XBTUSD['volume'][-2] == sum(df2['homeNotional'])
            assert XBTUSD['turnover'][-2] == sum(df2['foreignNotional'])

            assert XBTUSD.index[-1] == utc_datetime(2018, 1, 2, 12, 3)
            assert XBTUSD['high'][-1] == max(df3['price'])
            assert XBTUSD['low'][-1] == min(df3['price'])
            assert XBTUSD['open'][-1] == df3['price'][0]
            assert XBTUSD['close'][-1] == df3['price'][-1]
            assert XBTUSD['volume'][-1] == sum(df3['homeNotional'])
            assert XBTUSD['turnover'][-1] == sum(df3['foreignNotional'])

            TRXH19 = store['TRXH19']
            assert len(TRXH19) == 13

            assert TRXH19.index[-3] == utc_datetime(2018, 1, 2, 12, 1)
            assert TRXH19['high'][-3] == max(df4['price'])
            assert TRXH19['low'][-3] == min(df4['price'])
            assert TRXH19['open'][-3] == df4['price'][0]
            assert TRXH19['close'][-3] == df4['price'][-1]
            assert TRXH19['volume'][-3] == sum(df4['homeNotional'])
            assert TRXH19['turnover'][-3] == sum(df4['foreignNotional'])

            assert TRXH19.index[-2] == utc_datetime(2018, 1, 2, 12, 2)
            assert TRXH19['high'][-2] == max(df5['price'])
            assert TRXH19['low'][-2] == min(df5['price'])
            assert TRXH19['open'][-2] == df5['price'][0]
            assert TRXH19['close'][-2] == df5['price'][-1]
            assert TRXH19['volume'][-2] == sum(df5['homeNotional'])
            assert TRXH19['turnover'][-2] == sum(df5['foreignNotional'])

            assert TRXH19.index[-1] == utc_datetime(2018, 1, 2, 12, 3)
            assert TRXH19['high'][-1] == max(df6['price'])
            assert TRXH19['low'][-1] == min(df6['price'])
            assert TRXH19['open'][-1] == df6['price'][0]
            assert TRXH19['close'][-1] == df6['price'][-1]
            assert TRXH19['volume'][-1] == sum(df6['homeNotional'])
            assert TRXH19['turnover'][-1] == sum(df6['foreignNotional'])


def test_fullfill_kline() -> None:
    instruments_data = [
        {
            'symbol': "XBTUSD",
            'listing': '2016-05-04T12:00:00.000Z',
            'expiry': None
        },  # perpetual
        {
            'symbol': "TRXH19",
            'listing': '2018-12-12T06:00:00.000Z',
            'expiry': '2019-03-29T12:00:00.000Z'
        },  # listing
        {
            'symbol': "XRPZ17",
            'listing': '2017-09-14T08:00:00.000Z',
            'expiry': '2017-12-29T12:00:00.000Z'
        },  # finishing
        {
            'symbol': "XMRJ17",
            'listing': '2017-03-24T12:00:00.000Z',
            'expiry': '2017-04-28T12:00:00.000Z'
        }  # finished last time
    ]

    df1 = random_kline_data(2000, utc_datetime(2016, 6, 1, 23, 59))
    df2 = random_kline_data(2000, utc_datetime(2017, 1, 1, 23, 59))

    xbtusd = df1.append(df2)

    df4 = random_kline_data(2000, utc_datetime(2019, 1, 10))
    df5 = random_kline_data(1000, utc_datetime(2019, 1, 13, 23, 55))

    trxh19 = df4.append(df5)

    df6 = random_kline_data(2000, utc_datetime(2017, 9, 22))
    df7 = random_kline_data(1000, utc_datetime(2017, 12, 29, 12))

    xrpz17 = df6.append(df7)

    xmrj17 = random_kline_data_with_start_end(utc_datetime(2017, 3, 24, 12, 1), utc_datetime(2017, 4, 28, 12))

    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, INSTRUMENT_FILENAME), 'w') as f:
            json.dump(instruments_data, f)

        kline_file = os.path.join(tmp, KLINE_FILE_NAME)

        write_hdf(xbtusd, kline_file, "XBTUSD")
        write_hdf(trxh19, kline_file, "TRXH19")
        write_hdf(xrpz17, kline_file, "XRPZ17")
        write_hdf(xmrj17, kline_file, "XMRJ17")

        fullfill = KlineFullFill(tmp)

        fullfill.do_all()

        store = pandas.HDFStore(os.path.join(tmp, KLINE_FILE_NAME))

        XBTUSD = store['XBTUSD']

        assert len(XBTUSD) == 349200
        assert XBTUSD.index[0] == utc_datetime(2016, 5, 4, 12, 1)
        assert XBTUSD.index[-1] == utc_datetime(2017, 1, 2)
        asset_df_nan(XBTUSD, 1)
        compare_dataframe_time(XBTUSD, xbtusd, utc_datetime(2017, 1, 1, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XBTUSD, xbtusd, utc_datetime(2017, 1, 1, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XBTUSD, xbtusd, utc_datetime(2017, 1, 1, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XBTUSD, xbtusd, utc_datetime(2017, 1, 1, random.randint(0, 23), random.randint(0, 59)))

        compare_dataframe_time(XBTUSD, xbtusd, utc_datetime(2016, 6, 1, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XBTUSD, xbtusd, utc_datetime(2016, 6, 1, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XBTUSD, xbtusd, utc_datetime(2016, 6, 1, random.randint(0, 23), random.randint(0, 59)))

        compare_dataframe_filled(XBTUSD, utc_datetime(2016, 6, random.randint(2, 30),
                                                      random.randint(0, 23), random.randint(0, 59)),
                                 xbtusd, utc_datetime(2016, 6, 1, 23, 59))
        compare_dataframe_filled(XBTUSD, utc_datetime(2016, 6, random.randint(2, 30),
                                                      random.randint(0, 23), random.randint(0, 59)),
                                 xbtusd, utc_datetime(2016, 6, 1, 23, 59))

        # compare_dataframe_time(XBTUSD, xbtusd, )
        TRXH19 = store['TRXH19']
        assert len(TRXH19) == 47160
        assert TRXH19.index[0] == utc_datetime(2018, 12, 12, 6, 1)
        assert TRXH19.index[-1] == utc_datetime(2019, 1, 14)
        asset_df_nan(TRXH19, 1)
        compare_dataframe_time(TRXH19, trxh19, utc_datetime(2019, 1, 9, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(TRXH19, trxh19, utc_datetime(2019, 1, 9, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(TRXH19, trxh19, utc_datetime(2019, 1, 9, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(TRXH19, trxh19, utc_datetime(2019, 1, 9, random.randint(0, 23), random.randint(0, 59)))

        compare_dataframe_filled(TRXH19, utc_datetime(2019, 1, 11, random.randint(0, 23), random.randint(0, 59)),
                                 trxh19, utc_datetime(2019, 1, 10))
        compare_dataframe_filled(TRXH19, utc_datetime(2019, 1, 13, 23, 58),
                                 trxh19, utc_datetime(2019, 1, 13, 23, 55))

        XRPZ17 = store['XRPZ17']
        assert len(XRPZ17) == 152880
        asset_df_nan(XRPZ17, 1)
        compare_dataframe_time(XRPZ17, xrpz17, utc_datetime(2017, 9, 21, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XRPZ17, xrpz17, utc_datetime(2017, 9, 21, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XRPZ17, xrpz17, utc_datetime(2017, 9, 21, random.randint(0, 23), random.randint(0, 59)))
        compare_dataframe_time(XRPZ17, xrpz17, utc_datetime(2017, 9, 21, random.randint(0, 23), random.randint(0, 59)))

        compare_dataframe_filled(XRPZ17, utc_datetime(2017, 9, 23, random.randint(0, 23), random.randint(0, 59)),
                                 xrpz17, utc_datetime(2017, 9, 22))
        compare_dataframe_filled(XRPZ17, utc_datetime(2017, 9, 26, random.randint(0, 23), random.randint(0, 59)),
                                 xrpz17, utc_datetime(2017, 9, 22))

        XMRJ17 = store['XMRJ17']
        assert len(XMRJ17) == 50400

        compare_datafrome_index(xmrj17, XMRJ17, 0)
        compare_datafrome_index(xmrj17, XMRJ17, -1)
        compare_datafrome_index(xmrj17, XMRJ17, random.randint(1, len(XMRJ17)))
        compare_datafrome_index(xmrj17, XMRJ17, random.randint(1, len(XMRJ17)))
        compare_datafrome_index(xmrj17, XMRJ17, random.randint(1, len(XMRJ17)))
        compare_datafrome_index(xmrj17, XMRJ17, random.randint(1, len(XMRJ17)))
        compare_datafrome_index(xmrj17, XMRJ17, random.randint(1, len(XMRJ17)))
        store.close()
