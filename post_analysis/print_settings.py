#!/usr/bin/env python3.4
#
# post_analysis/print_settings.py
#
"""
Script which loops through femtolist and prints the configuration of each
analysis.
"""

from argparse import ArgumentParser
from pionpion import Femtolist
from pprint import pprint

parser = ArgumentParser()
parser.add_argument("filename", help="root filename to analyze")
args = parser.parse_args()

def recursive_print(obj, depth=0):
    prefix = '    ' * depth

    for k, v in obj.items():
        if isinstance(v, dict):
            print(prefix, k)
            recursive_print(v, depth+1)
        else:
            print(prefix, k, v)

for analysis in Femtolist(args.filename):
    print()
    print("\n■", analysis.GetName())
    pprint(analysis.metadata)
    # recursive_print(analysis.metadata)
