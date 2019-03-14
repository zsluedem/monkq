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
import random
import string
import sys
from contextlib import contextmanager
from typing import Any, Generator

from monkq.config import SETTING_MODULE, Setting


def random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


@contextmanager
def over_written_settings(settings: Setting, **options: Any) -> Generator[Setting, None, None]:
    for k, v in options.items():
        setattr(settings, k, v)

    yield settings


@contextmanager
def add_path(path: str) -> Generator[None, None, None]:
    """add a path in the sys path . Mostly for import"""
    sys.path.insert(0, path)
    yield
    sys.path.pop(0)


@contextmanager
def change_current_working_dir(target_dir: str) -> Generator[str, None, None]:
    current = os.getcwd()
    os.chdir(target_dir)
    yield target_dir
    os.chdir(current)


@contextmanager
def change_default_module_settings(module_setiings: str) -> Generator[None, None, None]:
    os.environ.setdefault(SETTING_MODULE, module_setiings)
    yield
    os.environ.pop(SETTING_MODULE)
