from MonkTrader.base_strategy import BaseStrategy


class MyStrategy(BaseStrategy):
    def setup(self):
        pass

    def on_trade(self, message):
        pass

    def tick(self, message):
        pass

    def handle_bar(self):
        pass
