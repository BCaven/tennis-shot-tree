"""
    Main driver for project,
    interface between the user and the algorithms




"""
import sys
from tennis_algorithm import human_vs_human, human_vs_alg, alg_vs_alg # modes
from tennis_algorithm import min_stat, max_stat, max_opponent_stat, min_opponent_stat # algorithms
from tree import sort_data
from parse_raw_data import get_point_data

def usage(return_val):
    print("""
Tennis Shot Tree
          USAGE: python3 main.py [FLAGS] [OPTIONS]
          --help            : print this message
          -h                : specify one of the players as human
          -max              : use a maximization algorithm
          -min              : use a minimization algorithm
          -stat STAT        : stat that the algorithms will either maximize or minimize
          -o                : use the stat on the opponent instead of ourselves
          -s    SCORE       : the score that the players are trying to reach
          -tree PATH        : path to the file used to build the tree
          -e    ENCODING    : encoding used on data file
          
          STAT
            num_hit         : the number of times a specific shot was seen
            num_success     : the number of times that shot was successful
            continue_prob   : probability that the point will continue after this shot
            winner_prob     : probability that the shot will be a winner
            error_prob      : probability that the shot will be an error

          DEFAULTS:
            SCORE           = 10
            PATH            = data/raw/charting-m-points-2010s.csv
            ENCODING        = windows-1252
          
          MINMAX ALGORITHMS
            The maximization and minimization algorithms operate on a single
            statistic which is specified by STAT
            Use of the -stat flag will have no impact when not using a
            maximization or minimization algorithm.
          
          NOTE:
            The -o flag must immediately follow either a -max or -min flag
            EXAMPLE: -max -o
          
          NOTE:
            For some reason, the match-charting-project encoded their files in windows-1252

""")
    sys.exit(return_val)


def main():
    """
        Interaction with the algorithms

    
    """
    # take command line arguments
    arguments = sys.argv[1:]
    humans = 0
    tree_path = 'data/raw/charting-m-points-2010s.csv'
    encoding = 'windows-1252' # disgusting, I know
    algs = []
    stats = []
    max_score = 10
    try:
        while arguments:
            current_arg = arguments.pop(0)
            if current_arg == '--help':
                usage(0)
            elif current_arg == '-h':
                humans += 1
            elif current_arg == '-max':
                if arguments[0] == '-o':
                    _ = arguments.pop(0)
                    print("adding max_opponent_stat to list of algs")
                    algs.append(max_opponent_stat)
                else:
                    print("adding max_stat to list of algs")
                    algs.append(max_stat)
            elif current_arg == '-min':
                if arguments[0] == '-o':
                    _ = arguments.pop(0)
                    print("adding min_opponent_stat to list of algs")
                    algs.append(min_opponent_stat)
                else:
                    print("adding min_stat to list of algs")
                    algs.append(min_stat)
            elif current_arg == '-stat':
                stats.append(arguments.pop(0))
            elif current_arg == '-s':
                max_score = int(arguments.pop(0))
            elif current_arg == '-tree':
                tree_path = arguments.pop(0)
            elif current_arg == '-e':
                encoding = arguments.pop(0)
            else:
                usage(1)
            
    except Exception as e:
        print(e)
        usage(1)
    
    # build tree
    print("building search tree from", tree_path)
    search_tree = sort_data(get_point_data(tree_path, encoding=encoding))
    print("done")
    if humans == 1:
        if len(algs) >= 1 and len(stats) >= 1:
            human_vs_alg(search_tree, algs[0], stats[0], max_score)
        else:
            usage(1)
    elif humans == 0:
        if len(algs) >= 2 and len(stats) >= 2:
            alg_vs_alg(search_tree, algs[:2], stats[:2], max_score)
        else:
            usage(1)
    else:
        human_vs_human(search_tree, max_score)

if __name__ == "__main__":
    main()