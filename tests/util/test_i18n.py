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
from unittest.mock import MagicMock, patch

from monkq.utils.i18n import LazyTranslation


def test_lazytranslation_not_setting() -> None:
    with patch("monkq.utils.i18n.gettext", MagicMock()) as mockg:
        mockg.find.return_value = None
        trans = LazyTranslation()
        trans.setup("CN")

        trans.gettext("hello")
        mockg.NullTranslations().gettext.assert_called()


def test_lazytranslation() -> None:
    with patch("monkq.utils.i18n.gettext", MagicMock()) as mockg:
        mockg.find.return_value = os.path.abspath(__file__)
        trans = LazyTranslation()
        trans.setup("CN")

        trans.gettext("hello")
        mockg.GNUTranslations().gettext.assert_called()
