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
import shutil
import sys
from typing import TypeVar

import click
import monkq
from logbook import StreamHandler
from monkq.data import DataProcessor
from monkq.exception import CommandError
from monkq.exchange.bitmex.data.download import BitMexDownloader
from monkq.exchange.bitmex.data.kline import (
    BitMexKlineTransform, KlineFullFill,
)
from monkq.utils.filefunc import assure_dir, make_writable
from monkq.utils.i18n import _

USERHOME = os.path.join(os.path.expanduser('~'), '.monk')

T_D = TypeVar("T_D", bound=DataProcessor)


@click.group()
@click.pass_context
def cmd_main(ctx: click.Context) -> None:
    StreamHandler(sys.stdout).push_application()


@cmd_main.command()
@click.help_option()
@click.option('--kind', default='trade', type=click.Choice(['quote', 'trade', 'instruments', 'kline']))
@click.option('--mode', default='hdf', type=click.Choice(['csv', 'tar', 'hdf']), help='Define the download mode')
@click.option('--dst_dir', default=os.path.expanduser('~/.monk/data'), type=str)
@click.pass_context
def download(ctx: click.Context, kind: str, mode: str, dst_dir: str) -> None:
    if kind == 'kline':
        kline_transform = BitMexKlineTransform(dst_dir, dst_dir)
        kline_transform.do_all()
        kline_fullfill = KlineFullFill(dst_dir)
        kline_fullfill.do_all()
    else:
        assure_dir(dst_dir)
        b = BitMexDownloader(kind, mode, dst_dir)
        b.do_all()


@cmd_main.command()
@click.help_option()
@click.option('--name', '-n', type=str)
@click.option('--directory', '-d', default=lambda: os.getcwd(), type=str)
@click.pass_context
def startstrategy(ctx: click.Context, name: str, directory: str) -> None:
    directory = os.path.abspath(directory)
    assert os.path.isdir(directory), _('You have to provide an exist directory')
    template_dir = os.path.join(monkq.__path__[0], 'config', 'project_template')  # type: ignore
    target_dir = os.path.join(directory, name)
    if os.path.exists(target_dir):
        raise CommandError(_("The project name has already been used"))
    assure_dir(target_dir)
    prefix_length = len(template_dir) + 1

    for root, dirs, files in os.walk(template_dir):
        relative_dir = root[prefix_length:]
        if relative_dir:
            create_dir = os.path.join(target_dir, relative_dir)
            if not os.path.exists(create_dir):
                os.mkdir(create_dir)

        for dirname in dirs[:]:
            if dirname.startswith('.') or dirname == '__pycache__':
                dirs.remove(dirname)

        for filename in files:
            if filename.endswith(('.pyo', '.pyc')):
                # Ignore some files as they cause various breakages.
                continue

            old_path = os.path.join(root, filename)

            if filename.endswith(('.py-tpl')):
                filename = filename.replace('.py-tpl', '.py')
                filename = filename.replace('@name@', name)
                new_path = os.path.join(target_dir, relative_dir, filename)
                with open(old_path) as template_f:
                    content = template_f.read()
                content = content.replace("@name@", name)
                with open(new_path, 'w') as new_file:
                    new_file.write(content)
            else:
                new_path = os.path.join(target_dir, relative_dir, filename)
                shutil.copyfile(old_path, new_path)
            shutil.copymode(old_path, new_path)
            make_writable(new_path)


if __name__ == '__main__':
    cmd_main()
