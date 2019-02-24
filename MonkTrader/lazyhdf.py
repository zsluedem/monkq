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

from typing import Dict, List

import pandas
from MonkTrader.exception import DataError
from MonkTrader.utils.i18n import _


class LazyHDFTableStore():
    def __init__(self, hdf_path: str):
        self.hdf_path = hdf_path
        self._cached: Dict[str, pandas.DataFrame] = dict()

    @property
    def cached_table(self) -> List[str]:
        return [key.strip('/') for key in self._cached.keys()]

    def get(self, key: str) -> pandas.DataFrame:
        if key in self._cached:
            return self._cached[key]
        else:
            try:
                df = pandas.read_hdf(self.hdf_path, key)
                self._cached[key] = df
                return df
            except KeyError:
                raise DataError(_("Not found hdf data {} in {}").format(key, self.hdf_path))
