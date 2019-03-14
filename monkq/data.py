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
from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Iterable, Iterator

from logbook import Logger
from monkq.exception import DataDownloadError
from monkq.utils.i18n import _

logger = Logger('data')


class Point(ABC):
    @abstractproperty
    def value(self) -> Any:
        raise NotImplementedError


class ProcessPoints(Iterable):
    def __iter__(self) -> Iterator[Point]:
        raise NotImplementedError()


class DataProcessor(ABC):
    @abstractmethod
    def process_points(self) -> ProcessPoints:
        raise NotImplementedError()

    @abstractmethod
    def process_one_point(self, point: Any) -> None:
        raise NotImplementedError()

    def do_all(self) -> None:
        try:
            for point in iter(self.process_points()):
                self.process_one_point(point)
        except DataDownloadError:
            logger.info(_('some exception occured when you download data at point {}. Check!!').format(point.value))
        self.last()

    def last(self) -> None:
        pass


class DownloadProcess(ABC):
    """
    Each download process should include two method -- "process" and "rollback".
    The "process" is to do the download main function.If there are any exceptions happened in
    "process"， "rollback" should be trigger and clean up the data in "process".

    classmethod "get_start" is used to get the start point from history.
    """

    def __init__(self, point: Point) -> None:
        ...  # pragma: no cover

    def process(self) -> None:
        """
        process the data after the raw_process data
        :return:
        """
        ...  # pragma: no cover

    def rollback(self) -> None:
        """
        If there is anything wrong happening in the process, the whole process would rollback
        :return:
        """
        ...  # pragma: no cover

    @classmethod
    def get_start(cls, obj: str) -> datetime.datetime:
        ...  # pragma: no cover


class DataLoader(ABC):
    @abstractmethod
    def load_instruments(self) -> None:
        raise NotImplementedError()

    def load(self) -> None:
        self.load_instruments()  # pragma: no cover
