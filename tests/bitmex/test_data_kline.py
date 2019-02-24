import datetime
import os
import tempfile
from unittest.mock import patch

import pandas
from MonkTrader.exchange.bitmex.const import TRADE_FILE_NAME
from MonkTrader.exchange.bitmex.data.kline import BitMexKlineTransform
from MonkTrader.exchange.bitmex.data.utils import (
    fullfill_1m_kline_with_start_end, trades_to_1m_kline, check_1m_data_integrity
)
from MonkTrader.exchange.bitmex.data.utils import trades_to_1m_kline, fullfill_1m_kline_with_start_end
from MonkTrader.utils import utc_datetime
from tests.bitmex.conftest import random_kline_data

from .conftest import random_kline_data, random_trade_frame


def test_trade_to_1m_kline() -> None:
    df1 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 12, 0, 1))
    df2 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 0, 1))
    df3 = random_trade_frame(10, pandas.Timestamp(2018, 1, 4, 12, 0, 1))

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
    df1 = random_kline_data(10, datetime.datetime(2018, 1, 1, 12, 10))

    assert check_1m_data_integrity(df1, datetime.datetime(2018, 1, 1, 12), datetime.datetime(2018, 1, 1, 12, 10))
    assert not check_1m_data_integrity(df1, datetime.datetime(2018, 1, 1, 12, 1),
                                       datetime.datetime(2018, 1, 1, 12, 10))

    assert not check_1m_data_integrity(df1, datetime.datetime(2018, 1, 1, 12), datetime.datetime(2018, 1, 1, 12, 12))


def test_fullfill_kline() -> None:
    k_df1 = random_kline_data(10, pandas.Timestamp(2018, 1, 2, 12, 30))
    k_df2 = random_kline_data(10, pandas.Timestamp(2018, 1, 6, 12, 30))

    kline_df = k_df1.append(k_df2)

    full_kline = fullfill_1m_kline_with_start_end(kline_df,
                                                  datetime.datetime(2018, 1, 1, 12),
                                                  datetime.datetime(2018, 1, 20, 12))

    assert len(full_kline) == 27360

    s1 = full_kline.loc[datetime.datetime(2018, 1, 2, 12, 29)]
    s2 = k_df1.loc[datetime.datetime(2018, 1, 2, 12, 29)]
    assert s1['close'] == s2['close']
    assert s1['open'] == s2['open']
    assert s1['high'] == s2['high']
    assert s1['low'] == s2['low']
    assert s1['volume'] == s2['volume']
    assert s1['turnover'] == s2['turnover']
    assert s1.name == s2.name

    s1 = full_kline.loc[datetime.datetime(2018, 1, 2, 12, 35)]
    s2 = k_df1.loc[datetime.datetime(2018, 1, 2, 12, 30)]

    assert s1['close'] == s2['close']
    assert s1['open'] == s2['open']
    assert s1['high'] == s2['high']
    assert s1['low'] == s2['low']
    assert s1['volume'] == 0
    assert s1['turnover'] == 0

    s1 = full_kline.loc[datetime.datetime(2018, 1, 6, 12, 25)]
    s2 = k_df2.loc[datetime.datetime(2018, 1, 6, 12, 25)]

    assert s1['close'] == s2['close']
    assert s1['open'] == s2['open']
    assert s1['high'] == s2['high']
    assert s1['low'] == s2['low']
    assert s1['volume'] == s2['volume']
    assert s1['turnover'] == s2['turnover']
    assert s1.name == s2.name

    s1 = full_kline.loc[datetime.datetime(2018, 1, 6, 12, 35)]
    s2 = k_df2.loc[datetime.datetime(2018, 1, 6, 12, 30)]

    assert s1['close'] == s2['close']
    assert s1['open'] == s2['open']
    assert s1['high'] == s2['high']
    assert s1['low'] == s2['low']
    assert s1['volume'] == 0
    assert s1['turnover'] == 0


def test_BitMexKlineTransform_from_scratch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, TRADE_FILE_NAME)

        df1 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 0, 1))
        df2 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 1, 1))
        df3 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 2, 1))
        hdf1 = df1.append(df2).append(df3)

        hdf1.to_hdf(target, "XBTUSD", mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

        df4 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 0, 1))
        df5 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 1, 1))
        df6 = random_trade_frame(10, utc_datetime(2018, 1, 1, 12, 2, 1))

        df7 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 0, 1))
        df8 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 1, 1))
        df9 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 2, 1))

        df10 = random_trade_frame(10, utc_datetime(2018, 1, 5, 12, 2, 1))

        hdf2 = df4.append(df5).append(df6).append(df7).append(df8).append(df9).append(df10)

        hdf2.to_hdf(target, 'TRXH19', mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

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

        hdf1.to_hdf(target, "XBTUSD", mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

        ori2 = random_trade_frame(10, utc_datetime(2018, 1, 1, 23, 50, 1))
        for i in range(kline_count - 1):
            ori2 = ori2.append(random_trade_frame(10, utc_datetime(2018, 1, 1, 23, 51 + i, 1)))
        df4 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 0, 1))
        df5 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 1, 1))
        df6 = random_trade_frame(10, utc_datetime(2018, 1, 2, 12, 2, 1))

        hdf2 = ori2.append(df4).append(df5).append(df6)

        hdf2.to_hdf(target, 'TRXH19', mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

        kline_df1 = random_kline_data(kline_count, utc_datetime(2018, 1, 1, 23, 59))
        kline_df2 = random_kline_data(kline_count, utc_datetime(2018, 1, 1, 23, 59))

        kline_df1.to_hdf(kline_hdf, "XBTUSD", mode='a',
                         format='table', data_columns=True,
                         complib='blosc', complevel=9, append=True)

        kline_df2.to_hdf(kline_hdf, "TRXH19", mode='a',
                         format='table', data_columns=True,
                         complib='blosc', complevel=9, append=True)

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
