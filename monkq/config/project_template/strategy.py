from monkq.base_strategy import BaseStrategy


class MyStrategy(BaseStrategy):
    async def setup(self):  # type:ignore
        pass

    async def on_trade(self, message):  # type:ignore
        pass

    async def tick(self, message):  # type:ignore
        pass

    async def handle_bar(self):  # type:ignore
        pass
