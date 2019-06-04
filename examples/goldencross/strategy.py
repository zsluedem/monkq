from monkq.base_strategy import BaseStrategy
from monkq.initer import Initer


class MyStrategy(BaseStrategy):
    async def setup(self):  # type:ignore
        self.bitmex = self.context.exchanges['bitmex']
        self.account = self.context.accounts['bitmex_account']
        self.instrument = await self.bitmex.get_instrument('XBTUSD')
        self.initer = Initer(self.context)
        self.initer.init_kline_freq("4H", instrument=self.instrument)
        self.initer.init_kline_freq("1H", instrument=self.instrument)
        self.initer.init_indicator("4H", self.instrument, "SMA", "SMA_4H", ['close'], timeperiod=20)
        self.initer.init_indicator("1H", self.instrument, "SMA", "SMA_1H", ['close'], timeperiod=20)

        self.holding = False

    def price_state(self, slow_line, fast_line):
        """
        :param slow_line:
        :param fast_line:
        :return: G -> golden cross, D -> death cross, L -> long state, S -> short state
        """
        if fast_line[0] < slow_line[0] and fast_line[1]> slow_line[1]:
            return "G"
        elif fast_line[0] < slow_line[0] and fast_line[1] < slow_line[1]:
            return "S"
        elif fast_line[0] > slow_line[0] and fast_line[1] > slow_line[1]:
            return "L"
        elif fast_line[0] > slow_line[0] and fast_line[1] < slow_line[1]:
            return "D"
        else:
            raise NotImplementedError()

    async def handle_bar(self):  # type:ignore
        sma_4h = self.initer.history_indicator("SMA_4H", 2)
        sma_1h = self.initer.history_indicator("SMA_1H", 2)
        if self.holding:
            if self.price_state(sma_4h, sma_1h) == "D":
                await self.bitmex.place_market_order(self.account, self.instrument, -10,
                                                     'short position because death cross')
        else:
            if self.price_state(sma_4h, sma_1h) == "G":
                await self.bitmex.place_market_order(self.account, self.instrument, 10,
                                                     'long position because golden cross')
