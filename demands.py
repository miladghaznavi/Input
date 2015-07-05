import sys
import argparse
import os.path
import csv

DELIM 	= " "
NEWLINE = "\n"

ARR_INDEX = 2
DUR_INDEX = 3

WORKLOAD_PY = 'python workload.py -a {a} -d {d} -n {n} -m {m} -s {s} -e {e} -o {o}'
OUTPUT_FILE = '%s/%s.txt'

def def_parser():
    parser = argparse.ArgumentParser(description='Generating workloads in terms of number of requests per !')
    parser.add_argument('-i', '--input', dest='i', help='Input request file', type=str, required=True)
    parser.add_argument('-n', '--number', dest='n', help='Maximum number of intervals (default is 2)', type=int, default=2)
    parser.add_argument('-m', '--mean', dest='m', help='Mean value (default is 5)', type=int, default=5)
    parser.add_argument('-s', '--std', dest='s', help='Standard deviation (default is 1)', type=int, default=1)
    parser.add_argument('-e', '--seed', dest='e', help='Random seed (default is 10)', type=int, default=10)
    parser.add_argument('-o', '--output', dest='o', help='Output Folder (default is working directory)', type=str, default='.')
    return parser

def parse_args(parser):
    opts = vars(parser.parse_args(sys.argv[1:]))
    if not os.path.isfile(opts['i']):
        raise Exception('File \'%s\' does not exist!' % opts['i'])
    return opts

def generate_shell_cmd(args, row, index):
    a = row[ARR_INDEX]
    d = row[DUR_INDEX]
    n = min(args['n'], int(d))
    o = OUTPUT_FILE % (args['o'], index)
    return WORKLOAD_PY.format(
        a = a,
        d = d,
        n = n,
        m = args['m'],
        s = args['s'],
        e = args['e'],
        o = o
    )

def main():
    try:
        args = parse_args(def_parser())
        with open(args['i']) as file:
            reader = csv.reader(file, delimiter=DELIM)
            count = 0
            for row in reader:
                cmd = generate_shell_cmd(args, row, count)
                os.system(cmd)
                count += 1

    except argparse.ArgumentError:
        print(argparse.error)

if __name__ == "__main__":
    main()