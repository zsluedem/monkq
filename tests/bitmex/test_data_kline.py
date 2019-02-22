import os
import tempfile

import pandas
from MonkTrader.exchange.bitmex.const import TRADE_FILE_NAME
from MonkTrader.exchange.bitmex.data.kline import BitMexKlineTransform
from tests.bitmex.conftest import random_kline_data

from .conftest import random_trade_frame


def test_BitMexKlineTransform_from_scratch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, TRADE_FILE_NAME)

        df1 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 12, 0, 1))
        df2 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 12, 1, 1))
        df3 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 12, 2, 1))
        hdf1 = df1.append(df2).append(df3)

        hdf1.to_hdf(target, "XBTUSD", mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

        df4 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 12, 0, 1))
        df5 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 12, 1, 1))
        df6 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 12, 2, 1))
        df7 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 0, 1))
        df8 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 1, 1))
        df9 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 2, 1))
        hdf2 = df4.append(df5).append(df6).append(df7).append(df8).append(df9)

        hdf2.to_hdf(target, 'ETHUSD', mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

        b = BitMexKlineTransform(tmp, tmp)
        b.do_all()

        with pandas.HDFStore(os.path.join(tmp, 'kline.hdf')) as store:
            XBTUSD = store['XBTUSD']

            assert XBTUSD.index[0] == pandas.Timestamp(2018, 1, 1, 12, 1)
            assert XBTUSD['high'][0] == max(df1['price'])
            assert XBTUSD['low'][0] == min(df1['price'])
            assert XBTUSD['open'][0] == df1['price'][0]
            assert XBTUSD['close'][0] == df1['price'][-1]
            assert XBTUSD['volume'][0] == sum(df1['homeNotional'])
            assert XBTUSD['turnover'][0] == sum(df1['foreignNotional'])

            assert XBTUSD.index[1] == pandas.Timestamp(2018, 1, 1, 12, 2)
            assert XBTUSD['high'][1] == max(df2['price'])
            assert XBTUSD['low'][1] == min(df2['price'])
            assert XBTUSD['open'][1] == df2['price'][0]
            assert XBTUSD['close'][1] == df2['price'][-1]
            assert XBTUSD['volume'][1] == sum(df2['homeNotional'])
            assert XBTUSD['turnover'][1] == sum(df2['foreignNotional'])

            assert XBTUSD.index[2] == pandas.Timestamp(2018, 1, 1, 12, 3)
            assert XBTUSD['high'][2] == max(df3['price'])
            assert XBTUSD['low'][2] == min(df3['price'])
            assert XBTUSD['open'][2] == df3['price'][0]
            assert XBTUSD['close'][2] == df3['price'][-1]
            assert XBTUSD['volume'][2] == sum(df3['homeNotional'])
            assert XBTUSD['turnover'][2] == sum(df3['foreignNotional'])

            ETHUSD = store['ETHUSD']

            assert ETHUSD.index[0] == pandas.Timestamp(2018, 1, 1, 12, 1)
            assert ETHUSD['high'][0] == max(df4['price'])
            assert ETHUSD['low'][0] == min(df4['price'])
            assert ETHUSD['open'][0] == df4['price'][0]
            assert ETHUSD['close'][0] == df4['price'][-1]
            assert ETHUSD['volume'][0] == sum(df4['homeNotional'])
            assert ETHUSD['turnover'][0] == sum(df4['foreignNotional'])

            assert ETHUSD.index[1] == pandas.Timestamp(2018, 1, 1, 12, 2)
            assert ETHUSD['high'][1] == max(df5['price'])
            assert ETHUSD['low'][1] == min(df5['price'])
            assert ETHUSD['open'][1] == df5['price'][0]
            assert ETHUSD['close'][1] == df5['price'][-1]
            assert ETHUSD['volume'][1] == sum(df5['homeNotional'])
            assert ETHUSD['turnover'][1] == sum(df5['foreignNotional'])

            assert ETHUSD.index[2] == pandas.Timestamp(2018, 1, 1, 12, 3)
            assert ETHUSD['high'][2] == max(df6['price'])
            assert ETHUSD['low'][2] == min(df6['price'])
            assert ETHUSD['open'][2] == df6['price'][0]
            assert ETHUSD['close'][2] == df6['price'][-1]
            assert ETHUSD['volume'][2] == sum(df6['homeNotional'])
            assert ETHUSD['turnover'][2] == sum(df6['foreignNotional'])

            assert ETHUSD.index[3] == pandas.Timestamp(2018, 1, 2, 12, 1)
            assert ETHUSD['high'][3] == max(df7['price'])
            assert ETHUSD['low'][3] == min(df7['price'])
            assert ETHUSD['open'][3] == df7['price'][0]
            assert ETHUSD['close'][3] == df7['price'][-1]
            assert ETHUSD['volume'][3] == sum(df7['homeNotional'])
            assert ETHUSD['turnover'][3] == sum(df7['foreignNotional'])

            assert ETHUSD.index[4] == pandas.Timestamp(2018, 1, 2, 12, 2)
            assert ETHUSD['high'][4] == max(df8['price'])
            assert ETHUSD['low'][4] == min(df8['price'])
            assert ETHUSD['open'][4] == df8['price'][0]
            assert ETHUSD['close'][4] == df8['price'][-1]
            assert ETHUSD['volume'][4] == sum(df8['homeNotional'])
            assert ETHUSD['turnover'][4] == sum(df8['foreignNotional'])

            assert ETHUSD.index[5] == pandas.Timestamp(2018, 1, 2, 12, 3)
            assert ETHUSD['high'][5] == max(df9['price'])
            assert ETHUSD['low'][5] == min(df9['price'])
            assert ETHUSD['open'][5] == df9['price'][0]
            assert ETHUSD['close'][5] == df9['price'][-1]
            assert ETHUSD['volume'][5] == sum(df9['homeNotional'])
            assert ETHUSD['turnover'][5] == sum(df9['foreignNotional'])


def test_BitMexKlineTransform_with_data() -> None:
    with tempfile.TemporaryDirectory() as tmp_input:
        kline_hdf = os.path.join(tmp_input, 'kline.hdf')

        target = os.path.join(tmp_input, TRADE_FILE_NAME)
        kline_count = 10

        ori1 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 23, 50, 1))
        for i in range(kline_count - 1):
            ori1 = ori1.append(random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 23, 51 + i, 1)))
        df1 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 0, 1))
        df2 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 1, 1))
        df3 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 2, 1))

        hdf1 = ori1.append(df1).append(df2).append(df3)

        hdf1.to_hdf(target, "XBTUSD", mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

        ori2 = random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 23, 50, 1))
        for i in range(kline_count - 1):
            ori2 = ori2.append(random_trade_frame(10, pandas.Timestamp(2018, 1, 1, 23, 51 + i, 1)))
        df4 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 0, 1))
        df5 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 1, 1))
        df6 = random_trade_frame(10, pandas.Timestamp(2018, 1, 2, 12, 2, 1))

        hdf2 = ori2.append(df4).append(df5).append(df6)

        hdf2.to_hdf(target, 'ETHUSD', mode='a',
                    format='table', data_columns=True,
                    complib='blosc', complevel=9, append=True)

        kline_df1 = random_kline_data(kline_count, pandas.Timestamp(2018, 1, 1, 23, 59))
        kline_df2 = random_kline_data(kline_count, pandas.Timestamp(2018, 1, 1, 23, 59))

        kline_df1.to_hdf(kline_hdf, "XBTUSD", mode='a',
                         format='table', data_columns=True,
                         complib='blosc', complevel=9, append=True)

        kline_df2.to_hdf(kline_hdf, "ETHUSD", mode='a',
                         format='table', data_columns=True,
                         complib='blosc', complevel=9, append=True)

        b = BitMexKlineTransform(tmp_input, tmp_input)
        b.do_all()

        with pandas.HDFStore(kline_hdf) as store:
            XBTUSD = store['XBTUSD']
            assert len(XBTUSD) == 13
            assert XBTUSD.index[-3] == pandas.Timestamp(2018, 1, 2, 12, 1)
            assert XBTUSD['high'][-3] == max(df1['price'])
            assert XBTUSD['low'][-3] == min(df1['price'])
            assert XBTUSD['open'][-3] == df1['price'][0]
            assert XBTUSD['close'][-3] == df1['price'][-1]
            assert XBTUSD['volume'][-3] == sum(df1['homeNotional'])
            assert XBTUSD['turnover'][-3] == sum(df1['foreignNotional'])

            assert XBTUSD.index[-2] == pandas.Timestamp(2018, 1, 2, 12, 2)
            assert XBTUSD['high'][-2] == max(df2['price'])
            assert XBTUSD['low'][-2] == min(df2['price'])
            assert XBTUSD['open'][-2] == df2['price'][0]
            assert XBTUSD['close'][-2] == df2['price'][-1]
            assert XBTUSD['volume'][-2] == sum(df2['homeNotional'])
            assert XBTUSD['turnover'][-2] == sum(df2['foreignNotional'])

            assert XBTUSD.index[-1] == pandas.Timestamp(2018, 1, 2, 12, 3)
            assert XBTUSD['high'][-1] == max(df3['price'])
            assert XBTUSD['low'][-1] == min(df3['price'])
            assert XBTUSD['open'][-1] == df3['price'][0]
            assert XBTUSD['close'][-1] == df3['price'][-1]
            assert XBTUSD['volume'][-1] == sum(df3['homeNotional'])
            assert XBTUSD['turnover'][-1] == sum(df3['foreignNotional'])

            ETHUSD = store['ETHUSD']
            assert len(ETHUSD) == 13

            assert ETHUSD.index[-3] == pandas.Timestamp(2018, 1, 2, 12, 1)
            assert ETHUSD['high'][-3] == max(df4['price'])
            assert ETHUSD['low'][-3] == min(df4['price'])
            assert ETHUSD['open'][-3] == df4['price'][0]
            assert ETHUSD['close'][-3] == df4['price'][-1]
            assert ETHUSD['volume'][-3] == sum(df4['homeNotional'])
            assert ETHUSD['turnover'][-3] == sum(df4['foreignNotional'])

            assert ETHUSD.index[-2] == pandas.Timestamp(2018, 1, 2, 12, 2)
            assert ETHUSD['high'][-2] == max(df5['price'])
            assert ETHUSD['low'][-2] == min(df5['price'])
            assert ETHUSD['open'][-2] == df5['price'][0]
            assert ETHUSD['close'][-2] == df5['price'][-1]
            assert ETHUSD['volume'][-2] == sum(df5['homeNotional'])
            assert ETHUSD['turnover'][-2] == sum(df5['foreignNotional'])

            assert ETHUSD.index[-1] == pandas.Timestamp(2018, 1, 2, 12, 3)
            assert ETHUSD['high'][-1] == max(df6['price'])
            assert ETHUSD['low'][-1] == min(df6['price'])
            assert ETHUSD['open'][-1] == df6['price'][0]
            assert ETHUSD['close'][-1] == df6['price'][-1]
            assert ETHUSD['volume'][-1] == sum(df6['homeNotional'])
            assert ETHUSD['turnover'][-1] == sum(df6['foreignNotional'])
