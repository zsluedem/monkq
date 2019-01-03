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

from MonkTrader.exchange.bitmex.auth import generate_signature, gen_header_dict, generate_expires, expire_ts
import time

secret = "chNOOS4KvNXR_Xq4k4c9qsfoKWvnDecLATCRlcBwyKDYnWgO"
api_id = "LAqUlngMIQkIUjXMUreyu3qn"

def test_generate_expires():
    assert generate_expires(123,123) == 246
    now = time.time()
    d = generate_expires() -now-expire_ts
    assert  d < 2


def test_generate_signature():
    assert generate_signature(secret, 'GET', 'http://testnet.bitmex.com/api/v1/instrument', 1518064236, '') == \
           'c7682d435d0cfe87c16098df34ef2eb5a549d4c5a3c2b1f0f77b8af73423bf00'


    assert generate_signature(
        secret, 'GET', '/api/v1/instrument?filter=%7B%22symbol%22%3A+%22XBTM15%22%7D', 1518064237, '') == \
           'e2f422547eecb5b3cb29ade2127e21b858b235b386bfa45e1c1756eb3383919f'

    assert generate_signature(secret,'POST','http://testnet.bitmex.com/api/v1/order',1518064238,
        '{"symbol":"XBTM15","price":219.0,"clOrdID":"mm_bitmex_1a/oemUeQ4CAJZgP3fjHsA","orderQty":98}') == \
           '1749cd2ccae4aa49048ae09f0b95110cee706e0944e6a14ad0b3a8cb45bd336b'

def test_gen_header_dict():
    assert gen_header_dict(api_id, secret, 'GET', 'http://testnet.bitmex.com/api/v1/instrument', '', 1518064236, 0) == \
           {
               "api-expires": '1518064236',
               "api-signature": 'c7682d435d0cfe87c16098df34ef2eb5a549d4c5a3c2b1f0f77b8af73423bf00',
               "api-key": api_id
           }