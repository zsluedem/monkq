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

import csv
import datetime
import gzip
import os
import tempfile

import pytest
import pytz
from MonkTrader.utils.filefunc import assure_dir, get_resource_path
from MonkTrader.utils.csv import CsvFileDefaultDict, CsvZipDefaultDict
from MonkTrader.utils.timefunc import is_aware_datetime


def test_assure_home() -> None:
    tmp_dir = tempfile.gettempdir()
    assert assure_dir(tmp_dir)

    with tempfile.NamedTemporaryFile() as f:
        with pytest.raises(NotADirectoryError):
            assure_dir(f.name)

    with tempfile.TemporaryDirectory() as tmp:
        assert assure_dir(tmp)

        new_p = os.path.join(tmp, 't/w')

        assert not assure_dir(new_p)

        assert assure_dir(new_p)


def test_csv_file_defaultdict() -> None:
    with tempfile.TemporaryDirectory() as tdir:
        headers = ['1', '2', '3']
        csv_d = CsvFileDefaultDict(tdir, headers)

        f1 = csv_d['123']
        assert isinstance(f1, csv.DictWriter)

        f1.writerow({'1': '3', '2': '2', '3': '1'})

        csv_d.close()

        assert os.path.isfile(os.path.join(tdir, '123.csv'))

        with open(os.path.join(tdir, '123.csv'), 'r') as f:
            content = f.read()

        assert content == "1,2,3{}3,2,1{}".format(CsvFileDefaultDict.CSVNEWLINE, CsvFileDefaultDict.CSVNEWLINE)


def test_csv_zip_default_dict() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        csv_d = CsvZipDefaultDict(tmp, ['1', '2', '3'])

        f = csv_d['file1']

        csv_d.writerow(f, ['1', '2', '3'])

        csv_d.close()
        assert os.path.isfile(os.path.join(tmp, 'file1.csv.gz'))
        with gzip.open(os.path.join(tmp, 'file1.csv.gz'), 'rb') as f2:
            content = f2.read()
        assert content == b"1,2,3\n1,2,3\n"


def test_aware_datetime() -> None:
    d1 = datetime.datetime(2018, 1, 1, 12, 0, 0)
    assert not is_aware_datetime(d1)

    d2 = datetime.datetime(2018, 1, 1, 12, tzinfo=pytz.utc)
    assert is_aware_datetime(d2)


def test_get_resource_path() -> None:
    current_file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(current_file_path)
    g = get_resource_path('test.txt')
    assert g == os.path.join(dir_path, 'resource', 'test.txt')

    g = get_resource_path('test.txt', 'test')
    assert g == os.path.join(dir_path, 'test', 'test.txt')
