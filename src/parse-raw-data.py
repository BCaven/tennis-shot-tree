#!/usr/bin/env python3
"""
Parse raw data into arrays of shots hit in each point
These arrays will have to be converted into trees (so each possible next shot can be determined) at some point
"""
import os
import sys
import csv

def usage(return_val):
    print("""
Raw Data Parser:
    USAGE: python3 parse-raw-data.py [FLAGS] [OPTIONS]
    -d DIRECTORY: directory of raw data
    -f FILE: specific file to parse
    -o DIRECTORY: directory to place output data in
    -t TASK: specify what the parser should do
    -h: print out this message

    DEFAULTS:
    RAW_DATA_DIRECTORY = data/raw/
    RAW_FILE = charting-m-points-2010s.csv
    OUTPUT_DIRECTORY = data/data-sorted-by-player/
    TASK = separate_by_player

    SUPPORTED TASKS:
    separate_by_player: read the raw file and sort match data into specific player files (appends to the file, so chance of duplicate lines)
    read_raw_data: print raw data dictionaries to stdin
    parse_all_data: split each point into individual shots and print the points to stdin
    """)
    sys.exit(return_val)

def separate_by_player(raw_path: str, output_dir: str, input_encoding='windows-1252', output_encoding='utf8'):
    """
        Separates raw data into files for individual players
        Each point is placed in the file for both players
    """
    with open(raw_path, 'r', encoding=input_encoding) as raw_file:
        csv_reader = csv.DictReader(raw_file)
        for row in csv_reader:
            for player in row['match_id'].split('-')[-2:]:
                output_file_name = output_dir + player.strip("_") + ".csv"
                with open(output_file_name, 'a', encoding=output_encoding) as output_file:
                    csv_writer = csv.DictWriter(output_file, fieldnames=row.keys())
                    if os.stat(output_file_name).st_size == 0:
                        # add header to csv file if it is a new file
                        csv_writer.writeheader()
                    csv_writer.writerow(row)
def read_raw_data(raw_path: str, encoding="utf8") -> dict:
    """
        Generates a dictionary of the next shot in the file
    """
    with open(raw_path, 'r', encoding=encoding) as raw_file:
        csv_reader = csv.DictReader(raw_file)
        for row in csv_reader:
            yield row

def parse_individual_point(raw_point: str, possible_shots="fbrsvzopuylmhijktq", types_of_faults="nwdxge!V", let="c", positioning_codes="+-=;^", possible_endings="CSR") -> list:
    """
        Parses point sentences into a list of individual shots

        RULES:
            Look at the "Instructions" section of MatchChart.xlsm
    """
    # going to build shots backwards, start at the end and go to the beginning
    individual_chars = [c for c in raw_point]
    shots = []
    while len(individual_chars) > 0:
        current_shot = ""
        while individual_chars[-1] not in possible_shots:
            current_shot = individual_chars.pop() + current_shot
            if not individual_chars:
                break
        if individual_chars:
            if individual_chars[-1] in possible_shots:
                current_shot = individual_chars.pop() + current_shot
        shots.insert(0, current_shot)
    return shots

def main():
    """
        Main function, hooray
    """
    raw_data_directory = "data/raw/"
    raw_data_file = "charting-m-points-2010s.csv"
    output_directory = "data/data-sorted-by-player/"
    task = "separate_by_player"
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
        elif current_arg == '-f':
            try:
                raw_data_file = arguments.pop(0)
            except:
                usage(1)
        elif current_arg == '-o':
            try:
                output_directory = arguments.pop(0)
            except:
                usage(1)
        elif current_arg == '-t':
            try:
                task = arguments.pop(0)
            except:
                usage(1)
        else:
            usage(1)

    if task == "separate_by_player":
        separate_by_player(raw_data_directory + raw_data_file, output_directory)
    elif task == "read_raw_data":
        for row in read_raw_data(raw_data_directory + raw_data_file):
            print(row)
    elif task == "parse_all_data":
        for row in read_raw_data(raw_data_directory + raw_data_file):
            first_serve = row["1st"]
            second_serve = row["2nd"]
            print(parse_individual_point(first_serve))
            if second_serve:
                print(parse_individual_point(second_serve))
    else:
        print("unknown task:", task)
        usage(1)
    # write them into an output file (json?)
if __name__ == "__main__":
    main()
