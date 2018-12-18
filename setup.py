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
# coding=utf8


from setuptools import (
    find_packages,
    setup,
)


KEYWORDS = ["MonkTrader", "quant", "finance", "trading"]
AUTHOR = "WILLQ"

with open('VERSION') as f:
    VERSION = f.read()

def parse_requirements(filename):
    require = []
    with open(filename) as f:
        for line in f:
            require.append(line)
    return require


requirements = parse_requirements("requirements.txt")

with open('description') as f:
    description = f.read()


setup(
    name='MonkTrader',
    version=VERSION,
    description=description,
    packages=find_packages(exclude=[]),
    author=AUTHOR,
    package_data={'': ['*.*']},
    install_requires=requirements,
    zip_safe=False,
    ext_modules=[],
    entry_points={
        "console_scripts": [
            "monktrader = MonkTrader.__main__:cmdEntry"
        ]
    },
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
