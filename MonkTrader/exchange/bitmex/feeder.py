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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import pickle
import pymongo
import pandas
from dateutil.relativedelta import relativedelta
from MonkTrader.data import DataFeeder


class PickleDataFeeder(DataFeeder):
    def __init__(self, directory):
        assert os.path.exists(directory)
        self.directory = directory
        self._data = dict()

        self.current_time = None

    def loaddata(self):
        for freq in ('1m', '5m'):
            with open(os.path.join(self.directory,f"{freq}.pkl"), 'rb') as f:
                data = pickle.load(f)
                del data['_id']
                data.set_index('timestamp', inplace=True)
                data['last'] = data['close']
                data['last'].fillna(method='ffill', inplace=True)
                self._data[freq] = data


    def update_date(self, current_time):
        self.current_time = current_time

    def history(self, freq, count, include_now=False):
        if include_now:
            end = self.current_time
            count -=1
        else:
            end = self.current_time - relativedelta(minutes=1)
        start = self.current_time - relativedelta(minutes=count)
        frame = self._data.get(freq)
        return frame[start: end]

    def get_last_price(self):
        return self._data['1m'].loc[self.current_time]['last']



class MongoDataFeeder(DataFeeder):
    def __init__(self, uri):
        self.client = pymongo.MongoClient(uri)
        self.data = dict()

    def loaddata(self):
        for freq  in ('1m', '5m'):
            col = self.client['bitmex'][freq]
            data = list(col.find({'symbol':"XBTUSD"}))
            self.data[freq]=pandas.DataFrame(data)


if __name__ == '__main__':
    a = MongoDataFeeder('localhost')
    a.loaddata()


