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
import gzip
import os
from typing import IO, List, Set


class CsvFileDefaultDict(dict):
    CSVNEWLINE = '\n'  # type: str

    def __init__(self, dir: str, fieldnames: List[str]) -> None:
        super(CsvFileDefaultDict, self).__init__()
        self.dir = dir
        self.default_factory = csv.DictWriter
        self.fieldnames = fieldnames
        self.file_set: Set = set()

    def __missing__(self, key: str) -> csv.DictWriter:
        f = open(os.path.join(self.dir, '{}.csv'.format(key)), 'w', newline=self.CSVNEWLINE)
        self.file_set.add(f)
        ret = self[key] = self.default_factory(f, fieldnames=self.fieldnames)
        ret.writeheader()
        return ret

    def close(self) -> None:
        for f in self.file_set:
            f.close()


class CsvZipDefaultDict(dict):
    CSVNEWLINE = '\n'  # type: str

    def __init__(self, dir: str, fieldnames: List[str], level: int = -1):
        super(CsvZipDefaultDict, self).__init__()
        self.dir = dir
        self.fieldnames = fieldnames
        self._level = level
        self.default_factory = gzip.open

        self.file_set = set()  # type: Set[IO]

    def __missing__(self, key: str) -> IO:
        f = gzip.open(os.path.join(self.dir, '{}.csv.gz'.format(key)), 'wb')
        self.writerow(f, self.fieldnames)
        self.file_set.add(f)
        ret = self[key] = f
        return ret

    def writerow(self, f: IO, row: List[str]) -> None:
        data = ','.join(row)
        data += self.CSVNEWLINE
        b_data = data.encode('utf8')
        f.write(b_data)

    def close(self) -> None:
        for f in self.file_set:
            f.close()
