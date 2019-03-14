#! python
import sys

from babel.messages.frontend import CommandLineInterface

width = '79'
if __name__ == '__main__':
    if sys.argv[1] == "extract":
        CommandLineInterface().run(['pybabel', 'extract', '--sort-by-file',
                                    '--project=monkq', 'monkq', '-o',
                                    'monkq/utils/translations/monkq.pot', '-w' ,width])
    elif sys.argv[1] == "init":
        CommandLineInterface().run(
            ['pybabel', 'init', '-l', sys.argv[2], '-i',
             'monkq/utils/translations/monkq.pot', '-d',
             'monkq/utils/translations', '-D', 'monkq', '-w' ,width])
    elif sys.argv[1] == 'compile':
        CommandLineInterface().run(
            ['pybabel', 'compile', '-d', 'monkq/utils/translations',
             '-D', 'monkq'])
    elif sys.argv[1] == 'update':
        CommandLineInterface().run(
            ['pybabel', 'update', '-i',
             'monkq/utils/translations/monkq.pot',
             '-D', 'monkq', '-d',
             'monkq/utils/translations', '-w' ,width])
    else:
        print("You have to provide the args choose from  extract, init, compile, update")
