import sys
import argparse
import json
import os
import os.path
import shutil
import subprocess
import ConfigParser

SUCCESS_CODE = 0

SAMPLE_PATH = 'sample.json'

# Data-center
DC = 'data-center'
DC_K = 'k'
DC_HOST_CAP = 'host-cap'
DC_LINK_CAP = 'link-cap'
DC_DEF_FILE = 'dc.txt'
DC_COMMAND = './dc -k {%s} -h {%s} -l {%s} -o %s' % (DC_K, DC_HOST_CAP, DC_LINK_CAP, DC_DEF_FILE)

# Service request
SERV_REQ = 'service-req'
SERV_REQ_NUMBER = 'number'
SERV_REQ_ARR_RATE = 'arr-rate'
SERV_REQ_DURATION = 'dur'
SERV_REQ_DEF_FILE = 'requests.txt'
SERV_REQ_COMMAND = 'python request.py -k {%s} -c {%s} -a {%s} -d {%s} -o %s' % \
                   (DC_K, SERV_REQ_NUMBER, SERV_REQ_ARR_RATE, SERV_REQ_DURATION, SERV_REQ_DEF_FILE)

# Workload
WL = 'workload'
WL_INT_NUMBER = 'interval-number'
WL_MEAN = 'mean'
WL_STD = 'std'
WL_REQ_SIZE = 'req-size'
WL_BWD_UNIT = 'bwd-unit'
WL_DEF_DIR = 'workload'
WL_DEF_FILE = 'demands.txt'
WL_COMMAND1 = 'python demands.py -i %s -n {%s} -m {%s} -s {%s} -o %s' % \
              (SERV_REQ_DEF_FILE, WL_INT_NUMBER, WL_MEAN, WL_STD, WL_DEF_DIR)
WL_COMMAND2 = 'python combine.py -r %s -w %s -s {%s} -b {%s} -o %s' % \
              (SERV_REQ_DEF_FILE, WL_DEF_DIR, WL_REQ_SIZE, WL_BWD_UNIT, WL_DEF_FILE)

# VNF
VNF = 'vnf'
VNF_CPU = 'cpu'
VNF_RAM = 'ram'
VNF_CAP = 'cap'

# Simulation
SIM = 'simulation'
SIM_TIME_SLOT = 'time-slot'
SIM_ENERGY_COST = 'energy-cost'
SIM_BWD_COST = 'bwd-cost'
SIM_VNF_REV = 'vnf-rev'
SIM_BWD_REV = 'bwd-rev'
SIM_REP_FLOW = 'rep-flows'
SIM_BALANCE_PARAM = 'balance'
SIM_DEF_FILE = 'config.ini'

def def_arg_parser():
    parser = argparse.ArgumentParser(description='Generating input of VNF placement simulation!')
    parser.add_argument('-c', '--config', dest='c', help='Config file (default is \'config.json\')', type=str, default='config.json')
    parser.add_argument('-w', '--wash', dest='w', action='store_true', help='Clean generated files!')
    return parser

def parse_args(parser):
    opts = vars(parser.parse_args(sys.argv[1:]))
    if not opts['w'] and not os.path.isfile(opts['c']):
        raise Exception('config file \'%s\' not found!' % opts['c'])
    return opts

def sample_dc():
    return {
        DC: {
            DC_K: 6,
            DC_HOST_CAP: 4,  # 4 core cpu
            DC_LINK_CAP: 125 # 250 (MB) Mega Byte
        }
    }

def sample_serv_req():
    return {
        SERV_REQ: {
            SERV_REQ_NUMBER: 1000,
            SERV_REQ_ARR_RATE: 1,    # 1 second
            SERV_REQ_DURATION: 1800, # 30 min in second
        }
    }

def sample_workload():
    return {
        WL: {
            WL_INT_NUMBER: 10,
            WL_MEAN: 20,
            WL_STD: 4,
            WL_REQ_SIZE: 0.1,# 0.1 MB (0.1 Mega Byte)
            WL_BWD_UNIT: 2.5,# 2.5 MB (2,5 Mega Byte)
        }
    }

def sample_vnf():
    return {
        VNF: {
            VNF_CPU: 1,
            VNF_RAM: 1000, # 1000 MB (1 GB)
            VNF_CAP: 4,    # Process 4 simultaneous traffic load of bwd_unit
                           # 4 * 2.5 MB = 10 MB = 10 Mega Byte
        }
    }

def sample_sim():
    return {
        SIM: {
            SIM_TIME_SLOT: 600, # 600 seconds = 10 min
            SIM_ENERGY_COST: 4, # 4 cents for a time slot
            SIM_BWD_COST: 1, # 1 cent for a unit of bandwidth for a time slot
            SIM_VNF_REV: 10, # 10 cents for a time slot
            SIM_BWD_REV: 4, # 4 cents for a unit of bandwidth for a time slot
            SIM_REP_FLOW: False, # not report
            SIM_BALANCE_PARAM: 3
        }
    }

def write_sample_config(path = SAMPLE_PATH):
    sample = {}
    sample.update(sample_dc())
    sample.update(sample_serv_req())
    sample.update(sample_workload())
    sample.update(sample_vnf())
    sample.update(sample_sim())

    with open(path, 'w') as outfile:
        json.dump(sample, outfile, indent=4)

def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    if process.returncode == SUCCESS_CODE:
        print process.stdout.read()
    else:
        print process.stderr.read()

def dc(data):
    cmd = DC_COMMAND.format(**data[DC])
    print cmd
    run_cmd(cmd)

def serv_req(data):
    new_data = data[SERV_REQ]
    new_data .update(data[DC])
    cmd = SERV_REQ_COMMAND.format(**new_data)
    print cmd
    run_cmd(cmd)

def workload(data):
    if not os.path.exists(WL_DEF_DIR):
        os.makedirs(WL_DEF_DIR)
    new_data = data[WL]
    cmd = WL_COMMAND1.format(**new_data)
    print cmd
    run_cmd(cmd)
    cmd = WL_COMMAND2.format(**new_data)
    print cmd
    run_cmd(cmd)

def write_conf(cnf, fp):
    """Write an .ini-format representation of the configuration state."""
    if cnf._defaults:
        fp.write("[%s]\n" % cnf.DEFAULTSECT)
        for (key, value) in cnf._defaults.items():
            fp.write("%s=%s\n" % (key, str(value).replace('\n', '\n\t')))
        fp.write("\n")
    for section in cnf._sections:
        fp.write("[%s]\n" % section)
        for (key, value) in cnf._sections[section].items():
            if key == "__name__":
                continue
            if (value is not None) or (cnf._optcre == cnf.OPTCRE):
                key = "=".join((key, str(value).replace('\n', '\n\t')))
            fp.write("%s\n" % (key))
        fp.write("\n")

def simulation(data):
    SIM_CONFIG_FILE = {
        'output': {
            'report-flow-files': False,
            'path': './'
        },
        'demands': {
            'path': WL_DEF_FILE
        },
        'vnf': {
            'cpu': data[VNF][VNF_CPU],
            'ram': data[VNF][VNF_RAM],
            'cap': data[VNF][VNF_CAP],
        },
        'datacenter': {
            'path' : DC_DEF_FILE,
            'bandwidth-unit': data[WL][WL_BWD_UNIT],
            'k': data[DC][DC_K],
        },
        'parameters': {
            'balance': data[SIM][SIM_BALANCE_PARAM],
            'bandwidth': data[SIM][SIM_BWD_COST],
            'energy': data[SIM][SIM_ENERGY_COST],
            'time-slot': data[SIM][SIM_TIME_SLOT]
        }
    }
    config = ConfigParser.ConfigParser()
    for section in SIM_CONFIG_FILE:
        config.add_section(section)
        for field in SIM_CONFIG_FILE[section]:
            config.set(section, field, SIM_CONFIG_FILE[section][field])

    with open(SIM_DEF_FILE, 'w') as conf_file:
        write_conf(config, conf_file)

def generate(args):
    data = {}
    with open(args['c']) as infile:
        data = json.load(infile)
    dc(data)
    serv_req(data)
    # workload(data)
    simulation(data)

def clean():
    try:
        os.remove(DC_DEF_FILE)
    except Exception as err:
        print(err)
    try:
        os.remove(SERV_REQ_DEF_FILE)
    except Exception as err:
        print(err)
    try:
        os.remove(SIM_DEF_FILE)
    except Exception as err:
        print(err)
    try:
        os.remove(WL_DEF_FILE)
    except Exception as err:
        print(err)
    try:
        shutil.rmtree(WL_DEF_DIR)
    except Exception as err:
        print(err)

def main():
    # write_sample_config()
    try:
        args = parse_args(def_arg_parser())
        if args['w']:
            clean()
        else:
            generate(args)
    except Exception as exc:
        print(exc)

if __name__ == "__main__":
    main()
