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

import argparse
from MonkTrader.config import MonkParser, MonkArgumentParser
from .common import random_string


plugin1_name = f'plugin1_{random_string(4)}'
plugin2_name = f'plugin2_{random_string(4)}'

def test_monk_argument_parser():
    parser = MonkArgumentParser()
    plugin1 = parser.add_plugin_parser(plugin1_name, description=f'{plugin1_name} description', help=f'{plugin1_name} help')
    assert isinstance(plugin1, MonkArgumentParser)

    plugin1_command_name = f'{plugin1_name}_test1'
    plugin1_command = plugin1.add_command(plugin1_command_name)

    plugin1_command.add_argument('-a', '--arg1', default=None)

    n = parser.parse_args([plugin1_name, '--arg1', '123'])

    assert n[plugin1_name]['arg1'] == 123

    # plugin2 = parser.add_plugin_parser('plugin2', description='plugin2 description', help='plugin2 help')
    # assert isinstance(plugin2, MonkArgumentParser)


def test_parser_cmd_parse():
    pass
    # args = ('--config', "monk.ini")
    # MonkParser.parse()

def test_parser_config_parse():
    pass

def test_parser_add_subcommand():
    pass

