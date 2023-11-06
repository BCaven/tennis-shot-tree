#!/usr/bin/env python3
"""
Parse raw data into arrays of shots hit in each point
These arrays will have to be converted into trees (so each possible next shot can be determined) at some point
"""
import os
import sys
import csv


ENDINGS = { # True means you just won the point, False means you just lost it
    False: "nwdxg!V@#", # oh no, you missed :c
    True: "*" # winners
}
MIN_REQUIRED_SHOTS = 5 # the cutoff for items in the tree, if there are fewer than this many of that shot, it will be ignored

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

class Shot:
    """
        class that describes each Node of a tree
        Contains:
            shot: str
            probability of being hit: float
            probability of success: float
            next shots: list
            probability that this shot will be a winner/cause an error: float
    """
    def __init__(self, shot: str, num_times_hit: int, num_times_success: int, next_shots: list):
        self.shot = shot
        self.num_hit = num_times_hit
        self.num_success = num_times_success
        self.next_shots = next_shots
    @classmethod
    def from_str(cls, raw_shot: str, good_endings="*", bad_endings="nwdxg!V@#"):
        """
            Build shot object from the raw string
            Assuming the shot is constructed as such:

        """
        # really there are just two things we need here: the shot, and the ending
        # split the shot from the ending, interpret the ending, call it a day
        # if the shot does not HAVE an ending, it was successful
        # split the shot
        ending = raw_shot[-1]
        cleaned_shot = raw_shot.strip(good_endings + bad_endings)
        if ending in good_endings:
            # you just won the point
            return cls(cleaned_shot, 1, 1, [])
            pass
        elif ending in bad_endings:
            # you just lost the point
            return cls(cleaned_shot, 1, 0, [])
        else:
            # you made the shot, but the point is still going
            return cls(cleaned_shot, 1, 1, [])

    def add_shot(self, hit: bool):
        """
            Another shot of this type was found, change its probability of being hit and probability of success

            I do not think this method is going to be used
            TODO: confirm deletion of this method (and remove it)
        """
        self.num_hit += 1
        self.num_success += 1 if hit else 0
    def update(self, shot):
        """
            Combine this node's data with another node's data
            returns itself (a.k.a. the updated node)
        """
        self.num_hit += shot.num_hit
        self.num_success += shot.num_success
        for shot in shot.next_shots:
            self.add_next_shot(shot)
        return self
    def add_next_shot(self, next_shot):
        """
            Add a next_shot
        """
        next_shot_indexes = [s.shot for s in self.next_shots]
        if next_shot.shot in next_shot_indexes:
            index = next_shot_indexes.index(next_shot.shot)
            self.next_shots[index].update(next_shot.num_hit, next_shot.num_success, next_shot.next_shots)
        else:
            self.next_shots.append(next_shot)

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

def parse_individual_point(raw_point: str, possible_shots="fbrsvzopuylmhijktq") -> list:
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
def sort_data(raw_data) -> list[Shot]:
    """
        Organize the data into a list of Shot objects
        Each Shot object in the list is the head of a Shot Tree
        This list should in theory only contain serves (represented by the numbers 4, 5, 6, and 0)
    """
    full_tree = []
    for row in raw_data:
        # assuming we are only getting data that we want
        full_tree_shots = [s.shot for s in full_tree]
        first_serve = parse_individual_point(row["1st"])
        prev_shot = Shot.from_str(first_serve.pop(0)) # get the first shot in the sequence (the serve)
        if prev_shot.shot not in full_tree_shots: # if the shot is not in the tree, add it to the tree (only starting points are stored in the tree)
            full_tree.append(prev_shot)
        else:
            # hey, this shot has already happened! add it to that tree node
            hit_index = full_tree_shots.index(prev_shot.shot)
            prev_shot = full_tree[hit_index].update(prev_shot)

        for shot in first_serve: # for the rest of them
            # go through and put them into the Shot tree
            current_shot = Shot.from_str(shot)
            prev_shot.add_next_shot(current_shot)
            prev_shot = current_shot

        # and repeat for the second serve
        second_serve = parse_individual_point(row["1st"])
        prev_shot = Shot.from_str(second_serve.pop(0)) # get the second shot in the sequence (the serve)
        if prev_shot.shot not in full_tree_shots:
            full_tree.append(prev_shot)
        else:
            hit_index = full_tree_shots.index(prev_shot.shot)
            prev_shot = full_tree[hit_index].update(prev_shot)
        for shot in second_serve:
            current_shot = Shot.from_str(shot)
            prev_shot.add_next_shot(current_shot)
            prev_shot = current_shot
    # return the tree
    return full_tree


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
            print(" ".join(parse_individual_point(first_serve)))
            if second_serve:
                print(" ".join(parse_individual_point(second_serve)))
    elif task == "print_stats":
        # sort points by player
        # then sort those points by serving vs returning
        # then put them into probability trees
        data = {}

        for row in read_raw_data(raw_data_directory + raw_data_file):
            if row["Serving"] not in returning_data:
                returning_data[row["Serving"]] = {}
            returning_data[row["Serving"]]
    elif task == "create_tree":
        # assuming the data directory and data file have been specified
        data = sort_data(read_raw_data(raw_data_directory + raw_data_file))
        # going to just print a few levels
        levels = 0
        current_level = data
        while levels < 5:
            chosen = current_level[0]
            for item in current_level:
                if item.num_hit > MIN_REQUIRED_SHOTS:
                    if chosen.num_success / chosen.num_hit < item.num_success / item.num_hit:
                        chosen = item
            print(chosen.shot, " ratio: ", chosen.num_success / chosen.num_hit)
            if chosen.next_shots:
                current_level = chosen.next_shots
            else:
                break # no more shots, so we are done

    else:
        print("unknown task:", task)
        usage(1)
    # write them into an output file (json?)
if __name__ == "__main__":
    main()
