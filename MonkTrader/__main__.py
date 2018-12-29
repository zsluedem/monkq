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
from MonkTrader.logger import console_log
from MonkTrader.config import settings
from MonkTrader.exchange.bitmex.data.kline import save_symbols, save_kline

from typing import List, Union, TypeVar


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
@click.option('--mongodb_uri', default='mongodb://127.0.0.1:27017', help="mongodb uri you want to download to")
@click.option('--active', default=True, type=click.BOOL ,help="download active or all symbols")
@click.option('--frequency', default="all", type=click.Choice(['all', '1m', '5m', '1h', '1d']))
def download(mongodb_uri, active, frequency):
    cli = pymongo.MongoClient(mongodb_uri)
    save_symbols(cli, active)

    if frequency == "all":
        save_kline(cli, '1m', active)
        save_kline(cli, '5m', active)
        save_kline(cli, '1h', active)
        save_kline(cli, '1d', active)
    else:
        save_kline(cli, frequency, active)



if __name__ == '__main__':
    cmd_main()