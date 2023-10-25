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
    """)
    sys.exit(return_val)

def separate_by_player(raw_path: str, output_dir: str):
    """
        Separates raw data into files for individual players
        Each point is placed in the file for both players
    """
    with open(raw_path, 'r', encoding='windows-1252') as raw_file:
        csv_reader = csv.DictReader(raw_file)
        for row in csv_reader:
            for player in row['match_id'].split('-')[-2:]:
                output_file_name = output_dir + player.strip("_") + ".csv"
                with open(output_file_name, 'a', encoding='utf8') as output_file:
                    csv_writer = csv.DictWriter(output_file, fieldnames=row.keys())
                    if os.stat(output_file_name).st_size == 0:
                        # add header to csv file
                        csv_writer.writeheader()
                    csv_writer.writerow(row)

def parse_individual_point(raw_point: str) -> list:
    """
        Parses point sentences into a list of individual shots

        RULES:
            First character is always a number (4, 5, 6)
            It can be followed by a '+'
            The return is a letter followed by two numbers (direction, depth)
            After that, the format is a letter followed by a number
                The letter is a shot, the number is the direction of the shot (1, 2, 3)
            The sentence ends with a character describing how the point ends (@, #, *)
            In the case of the point ending on an error, there will be an extra character immediately before which describes the type of error (n, w, d, x)
    """
    individual_chars = raw_points.split()

    return []


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
    else:
        print("unknown task:", task)
        usage(1)
    # write them into an output file (json?)
if __name__ == "__main__":
    main()
