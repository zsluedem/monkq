import asyncio
import ssl
from typing import Callable, Optional

from aiohttp import (  # type:ignore
    ClientResponse, ClientSession, TCPConnector,
)
from monkq.exchange.base.http import HTTPInterfaceBase
from monkq.exchange.okex.const import API_URL


class OKEXHttpInterface(HTTPInterfaceBase):
    def __init__(self, exchange_setting: dict, connector: TCPConnector, session: ClientSession,
                 ssl: Optional[ssl.SSLContext], proxy: Optional[str] = None,
                 loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        super(OKEXHttpInterface, self).__init__(exchange_setting, connector, session, ssl, proxy, loop)

        self.base_url = API_URL

    # async def get_account_info(self, auth_instance: AuthProtocol):
    #     resp = await self.curl(path=c.WALLET_INFO, auth_instance=auth_instance)
    #     return resp

    async def abnormal_status_checking(self, resp: ClientResponse, retry_callback: Callable) -> None:
        import logging
        logging.info(await resp.json())
