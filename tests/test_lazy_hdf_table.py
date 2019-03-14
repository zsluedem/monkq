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

import numpy as np
import pytest
from monkq.exception import DataError
from monkq.lazyhdf import LazyHDFTableStore
from monkq.utils.timefunc import utc_datetime
from tests.tools import get_resource_path


def test_lazy_hdf_table() -> None:
    store = LazyHDFTableStore(get_resource_path('test_table.hdf'))

    assert store.cached_table == []

    df1 = store.get('XBTZ15')

    assert df1.index[-1] == utc_datetime(2015, 12, 25, 12)
    assert df1.iloc[-1]['open'] == 453.11
    assert df1.iloc[-1]['close'] == 453.11
    assert df1.iloc[-1]['high'] == 453.11
    assert df1.iloc[-1]['low'] == 453.11
    assert df1.iloc[-1]['volume'] == 650.4802
    assert df1.iloc[-1]['turnover'] == 294739.1000

    assert df1.index[10] == utc_datetime(2015, 5, 29, 12, 11)
    assert np.isnan(df1.iloc[10]['open'])
    assert np.isnan(df1.iloc[10]['high'])
    assert np.isnan(df1.iloc[10]['close'])
    assert np.isnan(df1.iloc[10]['low'])
    assert df1.iloc[10]['volume'] == 0.0
    assert df1.iloc[10]['turnover'] == 0.0

    assert store.cached_table == ['XBTZ15']

    with pytest.raises(DataError):
        store.get("XBTUSD")
