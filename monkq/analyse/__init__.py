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
import pickle
import datetime
from typing import Optional
from monkq.context import Context


class Analyser():
    def __init__(self, result_file: str):
        with open(result_file, 'rb') as f:
            self.result_data = pickle.load(f)
        self.settings = self.result_data['settings']
        self.start_datetime = getattr(self.settings, 'START_TIME')
        self.end_datetime = getattr(self.settings, 'END_TIME')

    def plot_kline(self, exchange: str, freq: str,
                   start:Optional[datetime.datetime]=None, end:Optional[datetime.datetime]=None):
        if start is None:
            start = self.start_datetime
        if end is None:
            end = self.end_datetime
