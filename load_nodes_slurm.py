#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 15:18:24 2020

@author: tob
"""


import subprocess


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


def extract_nodes(nodelist):
    """
    Parameters
    ----------
    nodelist : STRING
        List of nodes as outputed by scontrol show job <jobid>.

    Returns
    -------
    nodes_listed : LIST
        List of nodes in form of hostnames.

    """
    if "[" in nodelist:
        prefix = nodelist.split("[")[0]
        nodes = nodelist.split("[")[1].strip("]")
        nodes_begin = nodes.split("-")[0]
        nodes_end = nodes.split("-")[1]
        nodes_listed = []
        for i in range(int(nodes_begin), int(nodes_end)+1):
            node_i = prefix + str(i)
            nodes_listed.append(node_i)
    else:
        nodes_listed = [nodelist]
    return nodes_listed


def list_to_dictionaries(lst_in, delimiter):
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
    for ientry in lst_in:
        n = ientry.split()
        for i in n:
            if delimiter in i:
                # print(i)
                tmp_key = i.split(delimiter)[0]
                tmp_val = i.split(delimiter)[1]
                # Multiple nodes are handled manually
                if tmp_key == "NodeList":
                    listed_nodes = extract_nodes(tmp_val)
                    d_entry[tmp_key] = listed_nodes
                else:
                    d_entry[tmp_key] = tmp_val
            else:
                pass
        param_table.append(d_entry)
        # Cleaning temporary dictionary is necessary.
        d_entry = {}
    return param_table


nodes_tmp = subprocess.run(["/usr/bin/scontrol", "show", "nodes"],
                           universal_newlines=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
cmd_nodes = nodes_tmp.stdout

# Splitting with 2 empty lines for iteration over entries from command
# output: scontrol show nodes
lines_nodes = cmd_nodes.split("\n\n")
lines_nodes.remove("")
# Populating list with data from command output
param_nodes = list_to_dictionaries(lines_nodes, "=")

jobs_tmp = subprocess.run(["/usr/bin/scontrol", "show", "jobs"],
                          universal_newlines=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
cmd_jobs = jobs_tmp.stdout

lines_jobs = cmd_jobs.split("\n\n")
try:
    lines_jobs.remove("")
except ValueError:
    pass

param_jobs = list_to_dictionaries(lines_jobs, "=")
# If no jobs are running populate with dummie entry
if len(param_jobs[0]) == 0:
    dummie = {}
    dummie["NodeList"] = "None"
    param_jobs = [dummie]

# Updating table with info about users
for i_node in param_nodes:
    for i_job in param_jobs:
        if (i_node["NodeName"] in i_job["NodeList"] and
            i_job["JobState"] == "RUNNING"):
            username = i_job["UserId"].split("(")[0]
            i_node.setdefault("UserList", []).append(username)

bprint('Node\tState\t\tUsers\tCores\tLoad\tRAM\tRAM usage', "BOLD")
for node in param_nodes:
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
