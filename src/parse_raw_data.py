"""
Parse raw data and perform associated tasks

"""
import os
import sys
import csv
from tree import sort_data, parse_individual_point

ENDINGS = { # True means you just won the point, False means you just lost it
    False: "nwdxg!V@#", # oh no, you missed :c
    True: "*" # winners
}
MIN_REQUIRED_SHOTS = 5 # the cutoff for items in the tree, if there are fewer than this many of that shot, it will be ignored
RESTRICTED_SEARCH = True
MAX_OPTIONS = 5
def usage(return_val):
    print("""
Raw Data Parser:
    USAGE: python3 parse-raw-data.py [FLAGS] [OPTIONS]
    -d DIRECTORY        : directory of raw data
    -f FILE             : file to parse
    -o DIRECTORY        : directory to place output data in
    -t TASK             : what the parser should do
    -e ENCODING         : encoding of the file being read in
    -eo ENCODING        : encoding of the output file
    -h                  : print out this message

    DEFAULTS:
    RAW_DATA_DIRECTORY  = data/raw/
    RAW_FILE            = charting-m-points-2010s.csv
    OUTPUT_DIRECTORY    = data/data-sorted-by-player/
    TASK                = separate_by_player

    SUPPORTED TASKS:
    separate_by_player  : read the raw file and sort match data into specific player files (appends to the file, so chance of duplicate lines)
    read_raw_data       : print raw data dictionaries to stdin
    parse_all_data      : split each point into individual shots and print the points to stdin
    create_tree         : generate a tree based on the given DIRECTORY/FILE specified by -d and -f
                          also allows the user to traverse the generated tree
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

def get_point_data(raw_data, encoding="utf8"):
    """
    returns just the point data, no distinction is made between points
    off first and second serves
    """
    raw = read_raw_data(raw_data, encoding=encoding)
    points = []
    for row in raw:
        points.append(row["1st"])
        points.append(row["2nd"])
    return points


def main():
    """
        Main function
    """
    raw_data_directory = "data/data-sorted-by-player/"
    raw_data_file = "Roger_Federer.csv"
    output_directory = "data/data-sorted-by-player/"
    task = "create_tree"
    encoding = "utf8"
    output_encoding = "utf8"
    # take command line arguments
    arguments = sys.argv[1:]
    try:
        while arguments:
            current_arg = arguments.pop(0)
            if current_arg == '-h':
                usage(0)
            elif current_arg == '-d':
                raw_data_directory = arguments.pop(0)
            elif current_arg == '-f':
                raw_data_file = arguments.pop(0)
            elif current_arg == '-o':
                output_directory = arguments.pop(0)
            elif current_arg == '-t':
                task = arguments.pop(0)
            elif current_arg == '-e':
                encoding  = arguments.pop(0)
            elif current_arg == '-eo':
                output_encoding = arguments.pop(0)
            else:
                usage(1)
    except Exception:
        usage(1)

    if task == "separate_by_player":
        separate_by_player(
            raw_data_directory + raw_data_file, 
            output_directory, 
            encoding=encoding,
            output_encoding=output_encoding)
    elif task == "read_raw_data":
        for row in read_raw_data(raw_data_directory + raw_data_file, encoding=encoding):
            print(row)
    elif task == "parse_all_data":
        for row in read_raw_data(raw_data_directory + raw_data_file, encoding=encoding):
            first_serve = row["1st"]
            second_serve = row["2nd"]
            print(" ".join(parse_individual_point(first_serve)))
            if second_serve:
                print(" ".join(parse_individual_point(second_serve)))
    
    elif task == "create_tree":
        data = sort_data(
            get_point_data(raw_data_directory + raw_data_file, encoding=encoding)
            )
        print(data.shot)
        done = False
        selected = data
        while not done:
            # allow the user to traverse the tree
            if not selected.next_shots:
                done = True
                break
            print("Possible next shots:")
            num_shown = 0
            for shot in selected.next_shots:
                if num_shown >= MAX_OPTIONS:
                    break
                if shot.num_hit > MIN_REQUIRED_SHOTS or not RESTRICTED_SEARCH:
                    print(f'{shot.shot}\tnumber of times hit: {shot.num_hit: 10.2f} | chance the point continues:{shot.continue_prob: 6.2f} | chance of winner:{shot.winner_prob: 6.2f} | chance of mistake:{shot.error_prob: 6.2f}')
                    num_shown+=1
            choice = input("Please choose a shot from the list of shots ('Q' to quit): ")
            if choice == 'Q':
                done = True
                break
            try:
                index = [s.shot for s in selected.next_shots].index(choice)
                selected = selected.next_shots[index]
            except ValueError:
                print("sorry that option was not found")
    else:
        print("unknown task:", task)
        usage(1)
    # write them into an output file (json?)
if __name__ == "__main__":
    main()
