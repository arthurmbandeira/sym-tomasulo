# -*- coding: utf-8 -*-

import sys
import getopt

from utils import *

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

    # input_ = []

    with open(f, 'r') as file:
        file = open(f, 'r')
        ins_list = [parse(line.replace(',', ' ').split()) for line in file]
        print ins_list
        # for line in file:
        #     p = parse(line.replace(',', ' ').split())
        #     print p.opcode
    file.close()


    # print input_

if __name__ == "__main__":
    main(sys.argv[1:])