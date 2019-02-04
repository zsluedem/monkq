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

import gettext
import os
from typing import IO, Optional
from warnings import warn

locale_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], "translations")


class LazyTranslation():
    def __init__(self) -> None:
        self._translation: Optional[gettext.NullTranslations] = None
        self._fp: Optional[IO] = None

    def setup(self, language: str) -> None:
        mofile = gettext.find("MonkTrader", locale_dir, [language])
        if mofile is None:
            warn("MonkTrader doesn't support the language {}. It would use English".format(language))
            self._translation = gettext.NullTranslations()
        else:
            self._fp = open(mofile, 'rb')
            self._translation = gettext.GNUTranslations(self._fp)  # type: ignore
            self._fp.close()

    def gettext(self, message: str) -> str:
        if self._translation is None:
            return message
        else:
            return self._translation.gettext(message=message)


translation: LazyTranslation = LazyTranslation()

_ = translation.gettext
