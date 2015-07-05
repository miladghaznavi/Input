import sys, math
import argparse
import os.path
import csv

DELIM = " "
NEWLINE = "\n"

WORKLOAD_FILE = '%s/%s.txt'

SRC_INDEX = 0
TRG_INDEX = 1
ARR_INDEX = 2

DEMAND_FORMAT = '%d %d %d %d %d\n'


def def_parser():
    parser = argparse.ArgumentParser(description='Generating Service Requests!')
    parser.add_argument('-r', '--request', dest='r', help='Requests file (default is requests.txt)', type=str, default='requests.txt')
    parser.add_argument('-w', '--workload', dest='w', help='Workload directory (default is .)', type=str, default='.')
    parser.add_argument('-s', '--size', dest='s', help='Request size (default is 0.1 MB)', type=float, default=0.1)
    parser.add_argument('-b', '--bwd', dest='b', help='Bandwidth unit (default is 2.50 Mb)', type=float, default=2.5)
    parser.add_argument('-o', '--output', dest='o', help='Output file name', type=str, default='demands.txt')
    return parser


def parse_args(parser):
    opts = vars(parser.parse_args(sys.argv[1:]))
    if not os.path.isfile(opts['r']):
        raise Exception('Request file \'%s\' does not exist!' % opts['r'])
    if not os.path.isdir(opts['w']):
        raise Exception('Workload directory \'%s\' does not exist!' % opts['w'])
    return opts


def workload_path(args, count):
    return WORKLOAD_FILE % (args['w'], count)


def parse(workload_file):
    content = workload_file.read()
    D = []
    for load in content.split(NEWLINE):
        if load == '':
            continue
        D.append(int(load))
    return D


def generate(args, row, count, D, mem):
    req_id = count
    src = int(row[SRC_INDEX])
    trg = int(row[TRG_INDEX])

    size = float(args['s'])
    bwd_unit = float(args['b'])

    arrivals = []
    time = int(row[ARR_INDEX])
    for load in D:
        units = math.ceil((float(load) * size) / bwd_unit)

        # if traffic increases
        while units > len(arrivals):
            arrivals.append(time)

        # if traffic decreases
        while units < len(arrivals):
            arr = arrivals.pop()
            dur = time - arr
            mem.append(
                {
                    'id': req_id,
                    'src': src,
                    'trg': trg,
                    'arr': arr,
                    'dur': dur
                }
            )
        time += 1

    while arrivals:
        arr = arrivals.pop()
        dur = time - arr
        mem.append(
            {
                'id': req_id,
                'src': src,
                'trg': trg,
                'arr': arr,
                'dur': dur
            }
        )


def demands_of(args, row, count, mem):
    with open(workload_path(args, count)) as workload_file:
        D = parse(workload_file)
        generate(args, row, count, D, mem)


def write_to_file(args, mem):
    with open(args['o'], 'w') as demands_file:
        for d in mem:
            demands_file.write(DEMAND_FORMAT % (
                d['id'],
                d['src'],
                d['trg'],
                d['arr'],
                d['dur'],
            ))


def main():
    try:
        args = parse_args(def_parser())
        with open(args['r']) as req_file:
            reader = csv.reader(req_file, delimiter=DELIM)
            count = 0
            mem = []
            for row in reader:
                demands_of(args, row, count, mem)
                count += 1
            write_to_file(args, sorted(mem, key=lambda item: (item['arr'])))
            print("%d Workloads have been generated!" % len(mem))
    except argparse.ArgumentError:
        print(argparse.error)
    except IOError as io_error:
        print(io_error)
    except Exception as exc:
        print(exc)

if __name__ == "__main__":
    main()
