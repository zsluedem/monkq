#! python
from babel.messages.frontend import CommandLineInterface
import sys

if __name__ == '__main__':
    if sys.argv[1] == "extract":
        CommandLineInterface().run(['pybabel', 'extract', '--sort-by-file',
                                    '--project=MonkTrader', 'MonkTrader', '-o',
                                    'MonkTrader/utils/translations/MonkTrader.pot'])
    elif sys.argv[1] == "init":
        CommandLineInterface().run(
            ['pybabel', 'init', '-l', sys.argv[2], '-i',
             'MonkTrader/utils/translations/MonkTrader.pot', '-d',
             'MonkTrader/utils/translations', '-D', 'MonkTrader'])
    elif sys.argv[1] == 'compile':
        CommandLineInterface().run(
            ['pybabel', 'compile', '-d', 'MonkTrader/utils/translations',
             '-D', 'MonkTrader'])
    elif sys.argv[1] == 'update':
        CommandLineInterface().run(
            ['pybabel', 'update', '-i',
             'MonkTrader/utils/translations/MonkTrader.pot',
             '-D', 'MonkTrader', '-d',
             'MonkTrader/utils/translations'])
    else:
        print("You have to provide the args choose from  extract, init, compile, update")
