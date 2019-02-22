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
import inspect
import os
import pathlib
import stat
from collections import defaultdict
from typing import IO, Any, List, Optional, Set, Type

from dateutil.tz import tzlocal


def assure_dir(directory: str) -> bool:
    """
    Assure dir is a directory.
    :param directory:
    :return: If dir is a directory , return True, else create the directory
        and return False
    :raise NotADirectoryError: if param dir is a file ,
        raise NotADirectoryError
    """
    path = pathlib.Path(directory)
    if path.is_dir():
        return True
    else:
        try:
            path.mkdir(parents=True)
        except FileExistsError:
            raise NotADirectoryError()
        return False


def is_aware_datetime(t: datetime.datetime) -> bool:
    return t.tzinfo is not None and t.tzinfo.utcoffset(t) is not None


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

    def __missing__(self, key:str) -> IO:
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


def local_tz_offset()->Optional[datetime.timedelta]:
    now = datetime.datetime.now(tzlocal())
    return now.utcoffset()


local_offset = local_tz_offset()
if local_offset is None:
    local_offset_seconds = 0.
else:
    local_offset_seconds = local_offset.total_seconds()


def get_resource_path(file: Optional[str] = None, prefix:str='resource') -> str:
    """
    This function would get the file path from the module which use this
    function. Supposed that:
    We have a dir like below:

    a_directory
        |
        |
        +-- __init__.py
        +-- a.py

    If we use this function in `a.py`, then this function would return
    `/path/to/a_directory/resource/{file}`

    :param file:
    :return:
    """
    outer_frame = inspect.getouterframes(inspect.currentframe())[1]
    file_path = outer_frame.filename
    dir_path = os.path.dirname(file_path)
    if file is None:
        return os.path.join(dir_path, prefix)
    else:
        return os.path.join(dir_path, prefix, file)


def make_writable(filename:str) ->None:
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)
