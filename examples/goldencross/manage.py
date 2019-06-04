import os

from monkq.strategy_cmd import cmd_main

os.environ.setdefault("MONKQ_SETTING_MODULE", 'goldencross_settings')
if __name__ == '__main__':
    cmd_main()
