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


cmdout = os.popen("/usr/bin/scontrol show nodes").read()


# Dzielenie w ten sposób powoduje, że iterujemy po wpisach z scontrol show nodes
lines = cmdout.split("\n\n")
lines.remove("")

param_table = []
d_entry = {}
for ientry in lines:
    n = ientry.split()
    for i in n:
        if "=" in i:
            # print(i)
            tmp_key = i.split("=")[0]
            tmp_val = i.split("=")[1]
            d_entry[tmp_key] = tmp_val
        else:
            pass
    param_table.append(d_entry)
    # Cleaning temporary dictionary is necessary.
    d_entry = {}

bprint('Node\tState\t\tCores\tLoad\tRAM\tRAM usage', "BOLD")
for node in param_table:
    n_state = node["State"]
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
    print("{} {:10}\t{}\t{}\t{}\t{:2.2%}".format(node["NodeName"], n_state,
                                             str(alloc) + "/" + str(ncpus),
                                             cpu_load, ram_full, ram_usage))
    pass


bprint('-------------------------------', "OKBLUE")
