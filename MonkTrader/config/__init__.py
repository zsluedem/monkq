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
import configparser

from typing import Optional, Type, Union, Tuple, List

class MonkArgumentParser(argparse.ArgumentParser):
    def __init__(self,*args, **kwargs):
        super(MonkArgumentParser, self).__init__(*args , **kwargs)

    def add_plugin_parser(self, plugin_name:str, description:Optional[str]=None, help:Optional[str]=None):
        return self.add_subparsers(title=plugin_name, description=description, dest=plugin_name, parser_class=MonkArgumentParser)

    def get_plugin_parser(self, plugin_name:str):
        pass


class MonkConfigParser(configparser.ConfigParser):
    pass

class Parser():
    def __init__(self):
        self.root_parser = MonkArgumentParser(prog="MonkTrader", description="MonkTrader is a crypto trading tool")

        self.sub_parsers = self.root_parser.add_subparsers(dest='subcommand')

        self.root_parser.add_argument('-c', '--config', help="config file path")

        self.result: Optional[argparse.Namespace] = None


    # def add_command(self, title: str, description: Optional[str] = None,
    #                 action: Optional[str, Type[argparse.Action]] = None, dest: str = None, require: bool = False,
    #                 help: Optional[str] = None) ->argparse._SubParsersAction:
    def add_command(self, name:str, help:Optional[str]):
        return self.sub_parsers.add_parser(name=name, help=help, dest=name)

    def add_plugin_parser(self, plugin_name:str, help:Optional[str]):
        return self.sub_parsers.add_parser(name=plugin_name, help=help)

    def parse(self, args: Union[List, Tuple, None] = None, namespace: Optional[argparse.Namespace] = None):
        if not self.result:
            self.result = self.root_parser.parse_args(args=args, namespace=namespace)
        return self.result

    def get_default_values(self, subcommand=None):
        return


MonkParser = Parser()


if __name__ == '__main__':
    s = MonkParser.add_plugin_command('test', 'a test help')
    s.add_argument('--asdf', help='asdv')
    s.add_argument('--dfbvrb', help='sdfb4erthb')


    k = MonkParser.add_plugin_command('test2', 'a test2 help')
    k.add_argument_group()
    k.add_argument('--asdf', help='asdv')
    k.add_argument('--rrr', help='sdfb4erthb')
    # a = MonkParser.parse(['--config', '/Users/willqiu/work/pull/MonkTrader/MonkTrader/config.py'])
    # print(a)

    h = MonkParser.parse(['--config','r/MonkTrader/config.py','test2','--rrr', 'asdvrw',])
    h = MonkParser.parse(['--help'])

    print(h)
