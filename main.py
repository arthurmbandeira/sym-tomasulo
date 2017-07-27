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
        # input_ = [line.strip() for line in file]
        for line in file:
            parse(line.replace(',', ' ').split())
    file.close()

    # print input_

if __name__ == "__main__":
    main(sys.argv[1:])