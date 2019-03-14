from monkq.base_strategy import BaseStrategy


class MyStrategy(BaseStrategy):
    def setup(self):  # type:ignore
        pass

    def on_trade(self, message):  # type:ignore
        pass

    def tick(self, message):  # type:ignore
        pass

    def handle_bar(self):  # type:ignore
        pass
