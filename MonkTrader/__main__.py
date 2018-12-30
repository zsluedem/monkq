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

import shutil
import click
import os
import pymongo
from MonkTrader.utils import assure_dir
from MonkTrader.logger import console_log
from MonkTrader.config import settings
from MonkTrader.exchange.bitmex.data.kline import save_symbols_json, save_kline
from MonkTrader.exchange.bitmex.data.quote import save_history

from typing import List, Union, TypeVar

USERHOME = os.path.join(os.path.expanduser("~"), '.monk')

@click.group()
@click.option('-c', '--config', type=str)
@click.pass_context
def cmd_main(ctx:click.Context, config):
    print(settings.START_TIME)
    pass


@cmd_main.command()
@click.option('-o', '--out', type=click.Path())
@click.pass_context
def gegnerate_settings(ctx, out):
    pass


@cmd_main.command()
@click.help_option()
@click.option('--kind', default="all", type=click.Choice(['all', 'quote', 'trade', 'kline', 'symbol']))
# @click.option('--mongodb_uri', default='mongodb://127.0.0.1:27017', help="mongodb uri you want to download to")
@click.option('--active', default=True, type=click.BOOL ,help="download active or all symbols")
@click.option('--mode', default="mongo", type=click.Choice(['mongo', 'csv', 'tar']), help="Define the download mode")
@click.option('--dst_dir', default=os.path.join(os.path.expanduser("~"), '.monk/data'), type=str)
def download(kind, active, mode, dst_dir):

    assure_dir(USERHOME)
    assure_dir(dst_dir)
    # cli = pymongo.MongoClient(mongodb_uri)
    # def save_all_klines():
    #     save_kline(cli, '1m', active)
    #     save_kline(cli, '5m', active)
    #     save_kline(cli, '1h', active)
    #     save_kline(cli, '1d', active)
    if kind == 'all':
        save_history('trade', mode, dst_dir)
        save_history('quote', mode, dst_dir)
        # save_all_klines()
        save_symbols_json(active, dst_dir)
    elif kind == 'quote':
        save_history('quote', mode, dst_dir)
    elif kind == 'trade':
        save_history('trade', mode, dst_dir)
    # elif kind == 'kline':
    #     save_all_klines()
    elif kind == 'symbol':
        save_symbols_json(active, dst_dir)
    else:
        raise NotImplementedError


if __name__ == '__main__':
    cmd_main()