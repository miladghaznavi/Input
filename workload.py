import sys, random, math
import argparse

DELIM 	= " "
NEWLINE = "\n"

def def_parser():
    parser = argparse.ArgumentParser(description='Generating workloads in terms of number of requests per !')
    parser.add_argument('-a', '--arrival', dest='a', help='Arrival time', type=int, required=True)
    parser.add_argument('-d', '--duration', dest='d', help='Duration', type=int, required=True)
    parser.add_argument('-n', '--number', dest='n', help='Number of intervals (default is 2)', type=int, default=2)
    parser.add_argument('-m', '--mean', dest='m', help='Mean value (default is 5)', type=int, default=5)
    parser.add_argument('-s', '--std', dest='s', help='Standard deviation (default is 1)', type=int, default=1)
    parser.add_argument('-e', '--seed', dest='e', help='Random seed (default is 10)', type=int, default=10)
    parser.add_argument('-o', '--output', dest='o', help='Output file name', type=str, default='workload.txt')
    return parser

def parse_args(parser):
    opts = vars(parser.parse_args(sys.argv[1:]))
    if opts['d'] < 2 or opts['d'] < opts['n'] != 0:
        raise Exception('Duration(%d) must be >= 2, and be greater than number of intervals (%d)' % (opts['d'], opts['n']))
    if opts['n'] == 0 or opts['n'] % 2 != 0:
        raise Exception('Number of intervals (%d) must be non-zero and divisible by 2!' % opts['n'])
    return opts

def generate(args):
    global DELIM, NEWLINE
    intervals = args['n']
    len       = args['d'] // intervals
    rem       = args['d'] % (len * intervals)
    mean      = args['m']
    std       = args['s']
    seed      = args['e']
    random.seed(seed)
    vals = []

    for i in range(0, intervals / 2):
        for j in range(len):
            vals.append(int(abs(math.ceil(random.gauss((i + 1) * mean, (i + 1) * std)))))

    for i in range(intervals / 2, 0, -1):
        for j in range(len):
            vals.append(int(abs(math.ceil(random.gauss(i * mean, i * std)))))

    for i in range(0, rem):
        vals.append(int(abs(math.ceil(random.gauss(mean, std)))))

    return vals

def write_to_file(file, vals):
    for val in vals:
        file.write(str(val))
        file.write(NEWLINE)

def main():
    try:
        args = parse_args(def_parser())
        vals = generate(args)
        with open(args['o'], 'w') as file:
            write_to_file(file, vals)

    except argparse.ArgumentError:
        print(argparse.error)
    except Exception as exc:
        print(exc)

if __name__ == "__main__":
    main()