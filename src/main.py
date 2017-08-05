# -*- coding: utf-8 -*-

import sys
import getopt
from utils import *
from tomasulo import *

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hf:", ["file"])
    except getopt.GetoptError:
        print('program.py -f <file>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('program.py -f <file>')
            sys.exit()
        elif opt in ("-f", "--file"):
            f = arg

    with open(f, 'r') as file:
        file = open(f, 'r')
        ins_list = [parse(line.replace(',', ' ').split()) for line in file if line[0] != '#']
    file.close()

    tom = Tomasulo(ins_list)

    # # Test basic operations: +, -, *, /
    # tom.write_memory(256, 6)
    # tom.write_memory(512, 3)

    # # Test logic operations: and, or, not
    # tom.write_memory(256, 0)
    # tom.write_memory(512, 1)
    
    tom.run()

if __name__ == "__main__":
    main(sys.argv[1:])