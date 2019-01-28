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

import os

import click
import MonkTrader
from MonkTrader.exchange.bitmex.data import BitMexDownloader
from MonkTrader.utils import assure_dir

USERHOME = os.path.join(os.path.expanduser('~'), '.monk')


@click.group()
@click.option('-c', '--config', type=str)
@click.pass_context
def cmd_main(ctx: click.Context, config):
    pass


@cmd_main.command()
@click.help_option()
@click.option('--kind', default='trade', type=click.Choice(['quote', 'trade', 'instruments']))
@click.option('--mode', default='csv', type=click.Choice(['mongo', 'csv', 'tar']), help='Define the download mode')
@click.option('--dst_dir', default=os.path.expanduser('~/.monk/data'), type=str)
@click.pass_context
def download(ctx: click.Context, kind: str, mode: str, dst_dir: str):
    if kind == 'instruments':
        pass
    else:
        dst_dir = os.path.join(dst_dir, '#'.join((mode, kind)))
    assure_dir(dst_dir)
    b = BitMexDownloader(kind, mode, dst_dir)
    b.do_all()


@cmd_main.command()
@click.help_option()
@click.option('--name', '-n', type=str)
@click.option('--directory', '-d', default=os.getcwd(), type=str)
def startstrategy(name: str, directory):
    assert os.path.isdir(directory), 'You have to provide an exist directory'
    template_dir = os.path.join(MonkTrader.__path__[0], 'config', 'project_template')


if __name__ == '__main__':
    cmd_main()
