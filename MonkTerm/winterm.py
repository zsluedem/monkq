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

import curses


class Logo():
    def __init__(self, stdscr):
        max_height, max_width = stdscr.getmaxyx()

        self.logo = self.read_logo()
        self.height = len(self.logo)

        self.width = max([len(i) for i in self.logo])

        assert max_width > self.width + 2

        x = int(( max_width - self.width ) / 2)

        for i, content in enumerate(self.logo):
            stdscr.addstr(i+1, x, content)
        stdscr.refresh()


    def read_logo(self):
        with open('logo') as f:
            return f.readlines()

class Window():
    def __init__(self, lines, cols, y, x, stdscr):
        assert cols >= 20
        self.win = stdscr.derwin(lines, cols, y, x)
        self.cols = cols
        self.win.border()
        self.win.refresh()

    def refresh_content(self, rstr, color=curses.COLOR_BLACK):
        self.win.clear()
        if len(rstr) > self.cols:
            rstr = 'Your str is too big'
        self.win.border()
        self.win.addstr(1, 1, rstr, curses.color_pair(color))
        self.win.refresh()

class QuoteWin():
    def __init__(self, stdsrc, symbol, y, x):
        self.symbol = symbol
        self.win =  Window(3, 40, y, x, stdsrc)

    def update_quote(self, price, volume):
        content = f'{self.symbol}  {price}  {volume}'
        self.win.refresh_content(content)

class DisWin():
    def __init__(self, stdsrc, y, x, warn=40, prefix="distance:  "):
        self.win = Window(3, 30, y, x, stdsrc)
        self.warn = warn
        self.prefix = prefix

    def update(self, dis):
        if dis > self.warn:
            self.win.refresh_content(self.prefix+str(round(dis,4)), curses.COLOR_GREEN)
        else:
            self.win.refresh_content(self.prefix+str(round(dis,4)), curses.COLOR_BLUE)


class MaWin():
    def __init__(self, stdsrc, y, x):
        self.win = stdsrc.derwin(7, 30, y, x)

    def update_ma(self, *args):
        self.win.clear()
        for i,v in enumerate(args):
            self.win.addstr(i+1, 1, f"MA{i}:{v}", curses.COLOR_CYAN)
        self.win.border()
        self.win.refresh()
