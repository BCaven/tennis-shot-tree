#!/usr/bin/env python3
"""
Parse raw data into arrays of shots hit in each point
These arrays will have to be converted into trees (so each possible next shot can be determined) at some point
"""
import sys
import csv

def usage(return_val):
    print("""
Raw Data Parser:
    USAGE: python3 parse-raw-data.py [-dfh]
    -d DIRECTORY: directory of raw data
    -f FILE: specific file to parse
    -h: print out this message""")
    sys.exit(return_val)

def raw_to_array(raw_path: str) -> list:
    """
        Converts raw strings to lists of individual shots
    """
    with open(raw_path, 'r') as raw_file:
        csv_reader = csv.DictReader(raw_file)
        for row in csv_reader:
            print(row)
    return []

def main():
    """
        Main function, hooray
    """
    raw_data_directory = "../data/raw/"
    raw_data_file = "charting-m-points-2010s.csv"
    # take command line arguments
    arguments = sys.argv[1:]
    while arguments:
        current_arg = arguments.pop(0)
        if current_arg == '-h':
            usage(0)
        elif current_arg == '-d':
            try:
                raw_data_directory = arguments.pop(0)
            except:
                usage(1)
        elif current_arg == 'f':
            try:
                raw_data_file = arguments.pop(0)
            except:
                usage(1)
        else:
            usage(1)

    # parse the strings
    parsed_data = raw_to_array(raw_data_directory + raw_data_file)
    # write them into an output file (json?)
