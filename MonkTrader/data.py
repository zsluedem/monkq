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

from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Iterator

from logbook import Logger
from MonkTrader.exception import DataDownloadError
from MonkTrader.utils.i18n import _

logger = Logger('data')


class Point(ABC):
    @abstractproperty
    def value(self) -> Any:
        raise NotImplementedError


class ProcessPoints(Iterator[Point]):
    def __iter__(self) -> Iterator[Point]:
        raise NotImplementedError


class DataDownloader(ABC):
    @abstractmethod
    def process_point(self) -> ProcessPoints:
        raise NotImplementedError

    @abstractmethod
    def download_one_point(self, point: Point) -> None:
        raise NotImplementedError

    def do_all(self) -> None:
        try:
            for point in self.process_point():
                self.download_one_point(point)
        except DataDownloadError:
            logger.info(_('some exception occured when you download data at point {}. Check!!'.format(point.value)))


class DataLoader(ABC):
    @abstractmethod
    def load_instruments(self) -> None:
        raise NotImplementedError()

    def load(self) -> None:
        self.load_instruments()


class DataFeeder():
    def loaddata(self) -> None:
        pass
