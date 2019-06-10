import ssl
from asyncio import AbstractEventLoop

from aiohttp import ClientSession, TCPConnector
from monkq.exchange.okex.auth import OKexAuth
from monkq.exchange.okex.http import OKEXHttpInterface

passphrase = '123456789'
api_key = 'ab58ebe8-3557-4521-9c2f-asf9341239f9'
api_secret = '5B07K919C77118F8E234K28344F82Q9D5'


async def test_okex_http_interface(loop: AbstractEventLoop):
    auth_instance = OKexAuth(api_key, api_secret, passphrase)
    ssl_context = ssl.create_default_context()
    connector = TCPConnector(keepalive_timeout=90)  # type:ignore
    session = ClientSession(loop=loop, connector=connector)

    interface = OKEXHttpInterface({}, connector, session, ssl_context, loop=loop)

    resp = await interface.get_account_info(auth_instance)
    import logging
    logging.warning(await resp.json())

    await session.close()
