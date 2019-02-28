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
from typing import Optional

from dateutil.parser import parse
from dateutil.tz import tzlocal
from pytz import utc


def utc_datetime(year: int, month: int, day: int, hour: int = 0,
                 minute: int = 0, second: int = 0, microsecond: int = 0) -> datetime.datetime:
    return datetime.datetime(year, month, day, hour, minute, second, microsecond, tzinfo=utc)


def parse_datetime_str(datetime_str: str) -> datetime.datetime:
    naive = parse(datetime_str, ignoretz=True)
    aware = naive.replace(tzinfo=utc)
    return aware


def is_aware_datetime(t: datetime.datetime) -> bool:
    return t.tzinfo is not None and t.tzinfo.utcoffset(t) is not None


def local_tz_offset() -> Optional[datetime.timedelta]:
    now = datetime.datetime.now(tzlocal())
    return now.utcoffset()


local_offset = local_tz_offset()
if local_offset is None:
    local_offset_seconds = 0.
else:
    local_offset_seconds = local_offset.total_seconds()
