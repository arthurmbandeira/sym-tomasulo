# -*- coding: utf-8 -*-

import sys
import getopt
from collections import deque
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

    # input_ = []

    # ins_queue = deque()

    with open(f, 'r') as file:
        file = open(f, 'r')
        ins_list = [parse(line.replace(',', ' ').split()) for line in file]

        # for line in file:
        #     ins_queue.append(parse(line.replace(',', ' ').split()))
    file.close()

    # print(ins_queue)

    Tomasulo(ins_list)


    # print input_

if __name__ == "__main__":
    main(sys.argv[1:])