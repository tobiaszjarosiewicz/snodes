#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 15:18:24 2020

@author: tob
"""


import os


class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNYELLOW = '\033[93m'
    FAILRED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def bprint(textinput, COLOUR):
    # Use getattr to pass attribute names
    COL1 = str(getattr(bcolors, COLOUR))
    print(COL1 + textinput + bcolors.ENDC)


def get_jobs_ids():
    """
    Get a list of active jobs.

    Returns
    -------
    job_ids : LIST
        List of jobs.
    """
    job_ids = []
    cmdout = os.popen("/usr/bin/sacct -X --allusers | grep RUNNING").read()
    lines = cmdout.split("\n")
    lines.remove("")
    for line in lines:
        job_ids.append(line.split()[0])
    return job_ids


def list_to_dictionaries(list_in, delimiter):
    """
    Parameters
    ----------
    list_in : LIST
        List containing values in a for of <key>delimiter<value>.
    delimiter : STRING
        Delimiter specifies which values will be added as keys and values.

    Returns
    -------
    param_table : List
        List of dictionaries.

    """
    param_table = []
    d_entry = {}
    for ientry in lines:
        n = ientry.split()
        for i in n:
            if delimiter in i:
                # print(i)
                tmp_key = i.split(delimiter)[0]
                tmp_val = i.split(delimiter)[1]
                d_entry[tmp_key] = tmp_val
            else:
                pass
        param_table.append(d_entry)
        # Cleaning temporary dictionary is necessary.
        d_entry = {}
    return param_table


cmd_nodes = os.popen("/usr/bin/scontrol show nodes").read()

# Splitting with 2 empty lines for iteration over entries from command
# output: scontrol show nodes
lines = cmd_nodes.split("\n\n")
lines.remove("")
# Populating list with data from command output
param_table = list_to_dictionaries(lines, "=")

cmd_nodes = os.popen("/usr/bin/scontrol show jobs").read()
lines = cmd_nodes.split("\n\n")
lines.remove("")

r_jobs = get_jobs_ids()

prep_out = ""
for job in r_jobs:
    prep_out += job

lines1 = prep_out.split("\n\n")

p_table2 = list_to_dictionaries(lines1, "=")

# Updating table with info about users
for i_node in param_table:
    for i_job in p_table2:
        if i_node["NodeName"] == i_job["NodeList"]:
            username = i_job["UserId"].split("(")[0]
            i_node.setdefault("UserList", []).append(username)

bprint('Node\tState\t\tUsers\tCores\tLoad\tRAM\tRAM usage', "BOLD")
for node in param_table:
    n_state = node["State"]
    try:
        a_users = node["UserList"]
    except KeyError:
        a_users = ["NONE"]
    usr_str = ''
    if len(a_users) == 1:
        usr_str = a_users[0]
    else:
        usr_str = len(a_users)
    ncpus = int(node["CoresPerSocket"])*2*int(node["Sockets"])
    cpu_load = node["CPULoad"]
    alloc = node["CPUAlloc"]
    ram_full = node["RealMemory"]
    ram_free = node["FreeMem"]
    ram_usage = (float(ram_full)-float(ram_free))/float(ram_full)
    """
    print(node["NodeName"], n_state, "   \t" + str(alloc) + "/" + str(ncpus),
          "\t" + str(cpu_load), "\t" + str(ram_full), "\t" + str(ram_usage))
    """
    print("{} {:10}\t{:3}\t{}\t{}\t{}\t{:2.2%}".format(node["NodeName"], n_state,
                                                     str(usr_str)[0:7],
                                                     str(alloc) + "/" + str(ncpus),
                                                     cpu_load,
                                                     ram_full,
                                                     ram_usage))
    pass


bprint('-------------------------------', "OKBLUE")
