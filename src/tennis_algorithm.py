"""
    Collection of algorithms that use the tree to decide what shot to hit

    Algorithms:
        minmax self: minimize or maximize your own statistic
        minmax opponent: minimize or maximize your opponent's statistic

    Available statistics:
        num_hit,
        num_success,
        continue_prob,
        winner_prob,
        error_prob        
        
"""
from tree import Shot
from random import randint

MIN_REQUIRED_SHOTS = 5 # the cutoff for items in the tree, if there are fewer than this many of that shot, it will be ignored
RESTRICTED_SEARCH = False
MAX_OPTIONS = 5
RAND_VAL_RESOLUTION = 1000

def max_stat(stat: str, shot: Shot, head: Shot) -> Shot:
    """
        Maximize the desired stat
    
    """
    if len(shot.next_shots) < MIN_REQUIRED_SHOTS:
        shot = breadth_first_search(shot.shot, head)
        if shot == head:
            print("The BFS failed to find a shot of that type")
            return head
        else:
            print("The BFS has found an equivalent node")

    next_shot = shot.next_shots[0]
    max = next_shot.get_stat(stat)
    for next in shot.next_shots:
        if next.get_stat(stat) > max:
            max = next.get_stat(stat)
            next_shot = next
    return next_shot

def min_stat(stat: str, shot: Shot, head: Shot) -> Shot:
    """
        Minimize the desired stat
    """
    if len(shot.next_shots) < MIN_REQUIRED_SHOTS:
        shot = breadth_first_search(shot.shot, head)
        if shot == head:
            print("The BFS failed to find a shot of that type")
            return head
        else:
            print("The BFS has found an equivalent node")

    next_shot = shot.next_shots[0]
    min = next_shot.get_stat(stat)
    for next in shot.next_shots:
        if next.get_stat(stat) < min:
            min = next.get_stat(stat)
            next_shot = next
    return next_shot

def max_opponent_stat(stat: str, shot: Shot, head: Shot) -> Shot:
    """
        Pick a shot that maximizes the opponent's stat

        i.e. pick a stat that maximizes the likelyhood of the opponent hitting an error
    
        Looking for the shot with the highest minimum
    """
    
    our_choice = shot.next_shots[0]
    min = our_choice.next_shots[0]
    for our_option in shot.next_shots:
        opponent_option = min_stat(stat, our_option, head)
        if opponent_option.get_stat(stat) < min.get_stat(stat):
            min = opponent_option
            our_choice = our_option
    return our_choice

def min_opponent_stat(stat: str, shot: Shot, head: Shot) -> Shot:
    """
        Pick the shot that minimizes the opponent's stats

        Looking for the shot with the lowest maximum
    """
    our_choice = shot.next_shots[0]
    max = our_choice.next_shots[0]
    for our_option in shot.next_shots:
        opponent_option = max_stat(stat, our_option, head)
        if opponent_option.get_stat(stat) < max.get_stat(stat):
            max = opponent_option
            our_choice = our_option
    return our_choice

def breadth_first_search(shot:str, tree: Shot) -> Shot:
    """
        Search the tree for a node that is this shot

        Useful if the current tree does not have the desired shot in its tree
    
    """
    search_list = [tree]
    while search_list:
        current = search_list.pop(0)
        if current.shot == shot:
            return current
        for next in current.next_shots:
            if next.next_shots: # if the next shot is not the end of the tree, 
                                # add it to the list of nodes to be expanded
                search_list.append(next)
    print("BFS failed to find shot of type:", shot)
    return tree # if we couldnt find one, just return the head of the tree
                # this should never happen

def human_vs_human(search_tree: Shot, max_score: int=10):
    """
        No AI involved, just the same ol' story of humans playin' humans
    """
    side = 1 # 1 is deuce, -1 is ad
    score = (0, 0) # tuple containing the score of the players
                   # NOTE: in "real" tennis, the score is structured in points, games, and sets
                   #       however, to simplify, I am going to use 10-point tie-break scoring
    server = 1 if randint(0, 1) == 0 else -1 # 1 is p1, -1 is p2, randomized who starts serving

    while score[0] < max_score and score[1] < max_score:
        p1_score, p2_score = score
        print("Score: ", p1_score, "-", p2_score)
        print("Server: Player", 1 if server > 0 else 2)
        point_finished = False
        next = server
        current_shot = search_tree
        while not point_finished: # point
            print("Player ", 1 if next > 0 else 2, "'s turn:", sep="")
            if len(current_shot.next_shots) < MIN_REQUIRED_SHOTS:
                current_shot = breadth_first_search(current_shot.shot, search_tree)
                if current_shot == search_tree:
                    print("The BFS failed to find a shot of that type")
                else:
                    print("The BFS has found an equivalent node")
            print("Options:")
            num_shown = 0
            for shot in current_shot.next_shots:
                if num_shown >= MAX_OPTIONS:
                    break
                if shot.num_hit > MIN_REQUIRED_SHOTS or not RESTRICTED_SEARCH:
                    print(f'{shot.shot}\tnumber of times hit: {shot.num_hit: 10.2f} | chance the point continues:{shot.continue_prob: 6.2f} | chance of winner:{shot.winner_prob: 6.2f} | chance of mistake:{shot.error_prob: 6.2f}')
                    num_shown+=1
            choice = input("Please choose a shot from the list of shots: ")
            try:
                shot_index = [s.shot for s in current_shot.next_shots].index(choice)
                current_shot = current_shot.next_shots[shot_index]
            except ValueError:
                print("sorry that option was not found")
                continue
            
            # now check if the shot succeeded
            chance_of_making_the_shot = randint(0, RAND_VAL_RESOLUTION) / RAND_VAL_RESOLUTION
            if chance_of_making_the_shot > current_shot.error_prob:
                # yay you made the shot, now check if it was a winner
                chance_of_winner = randint(0, RAND_VAL_RESOLUTION) / RAND_VAL_RESOLUTION
                if chance_of_winner < current_shot.winner_prob:
                    # yay you hit a winner
                    point_finished = True
                    if next == 1:
                        p1_score += 1
                    else:
                        p2_score += 1
                # if you did not hit a winner and did not miss it, then the point just continues
            else:
                # oh no, you missed it
                point_finished = True
                if next == 1:
                    p2_score += 1
                else:
                    p1_score += 1
            
            next *= -1
            

        score = (p1_score, p2_score)
        side *= -1 # switch sides
        if p1_score + p2_score == 1:
            server *= -1 # switch server if it was the first point
        elif (p1_score + p2_score - 1) % 2 == 0:
            server *= -1
    print("Final Score:")
    print(score[0], "-", score[1])
    if score[0] > score[1]:
        print("Player 1 wins!")
    else:
        print("Player 2 wins!")

def human_vs_alg(search_tree: Shot, algorithm, stat: str="continue_prob", max_score: int=10):
    """
        TODO: rework how algorithms are passed to this function

        Interactive point play


        Important things to remember:
        In tennis the server switches sides after each point (alternate deuce/ad)
        However, the serves are coded wide/body/T 
            which means a wide serve on the deuce side goes to the opponent's FOREHAND (right side)
            but the same wide serve on the ad side will go to the opponent's BACKHAND (left side)
            And it flips if one of the opponents is left-handed
        
        10-point tie-break scoring:
            Decide who serves first
            Person serving first serves for one point
            after that, each player serves twice before switching who serves
            Example: p1 serves, p2 serves, p2 serves, p1 serves, p1 serves, etc
        
        If the score is 9 - 9, the next point wins.
        This is generally not how scoring works in the actual game (most tournaments will play win-by-two)
        but for this demonstration it will work well enough
    """
    side = 1 # 1 is deuce, -1 is ad
    score = (0, 0) # tuple containing the score of the players
                   # NOTE: in "real" tennis, the score is structured in points, games, and sets
                   #       however, to simplify, I am going to use 10-point tie-break scoring
    server = 1 if randint(0, 1) == 0 else -1 # 1 is p1, -1 is p2, randomized who starts serving

    while score[0] < max_score and score[1] < max_score:
        p1_score, p2_score = score
        print("Current score: ", p1_score, "-", p2_score)
        point_finished = False
        next = server
        current_shot = search_tree
        while not point_finished: # point
            if next == 1: # human picks shot
                print("Player ", 1 if next > 0 else 2, "'s turn:", sep="")
                if len(current_shot.next_shots) < MIN_REQUIRED_SHOTS:
                    current_shot = breadth_first_search(current_shot.shot, search_tree)
                    if current_shot == search_tree:
                        print("The BFS failed to find a shot of that type")
                    else:
                        print("The BFS has found an equivalent node")
                print("Options:")
                num_shown = 0
                for shot in current_shot.next_shots:
                    if num_shown >= MAX_OPTIONS:
                        break
                    if shot.num_hit > MIN_REQUIRED_SHOTS or not RESTRICTED_SEARCH:
                        print(f'{shot.shot}\tnumber of times hit: {shot.num_hit: 10.2f} | chance the point continues:{shot.continue_prob: 6.2f} | chance of winner:{shot.winner_prob: 6.2f} | chance of mistake:{shot.error_prob: 6.2f}')
                        num_shown+=1
                choice = input("Please choose a shot from the list of shots: ")
                try:
                    shot_index = [s.shot for s in current_shot.next_shots].index(choice)
                    current_shot = current_shot.next_shots[shot_index]
                except ValueError:
                    print("sorry that option was not found")
                    continue
            elif next == -1: # alg picks shot
                current_shot = algorithm(stat, current_shot, search_tree)
                if current_shot == search_tree:
                    print("The BFS failed to find a shot of that type...")
                else:
                    print("alg hit:", current_shot.shot)
            else:
                print("oh no, something went wrong")
            
            # now check if the shot succeeded
            chance_of_making_the_shot = randint(0, RAND_VAL_RESOLUTION) / RAND_VAL_RESOLUTION
            if chance_of_making_the_shot > current_shot.error_prob:
                # yay you made the shot, now check if it was a winner
                chance_of_winner = randint(0, RAND_VAL_RESOLUTION) / RAND_VAL_RESOLUTION
                if chance_of_winner < current_shot.winner_prob:
                    # yay you hit a winner
                    point_finished = True
                    if next == 1:
                        p1_score += 1
                    else:
                        p2_score += 1
                # if you did not hit a winner and did not miss it, then the point just continues
            else:
                # oh no, you missed it
                point_finished = True
                if next == 1:
                    p2_score += 1
                else:
                    p1_score += 1
            
            next *= -1
            

        score = (p1_score, p2_score)
        side *= -1 # switch sides
        if p1_score + p2_score == 1:
            server *= -1 # switch server if it was the first point
        elif (p1_score + p2_score - 1) % 2 == 0:
            server *= -1
    
    print("Final Score:")
    print(score[0], "-", score[1])
    if score[0] > score[1]:
        print("Player 1 wins!")
    else:
        print("Player 2 wins!")

# TODO: write alg-vs-alg function
def alg_vs_alg(search_tree: Shot, algorithms: list, stat: list[str, str]=["continue_prob", "continue_prob"], max_score: int=10):
    """
        TODO: rework how algorithms are passed to this function

        Same rules as human_vs_human and human_vs_alg
    """
    side = 1 # 1 is deuce, -1 is ad
    score = (0, 0) # tuple containing the score of the players
                   # NOTE: in "real" tennis, the score is structured in points, games, and sets
                   #       however, to simplify, I am going to use 10-point tie-break scoring
    server = 1 if randint(0, 1) == 0 else -1 # 1 is p1, -1 is p2, randomized who starts serving

    while score[0] < max_score and score[1] < max_score:
        p1_score, p2_score = score
        point_finished = False
        next = server
        current_shot = search_tree
        while not point_finished: # point
            alg = 0 if next > 0 else 1
            current_shot = algorithms[alg](stat[alg], current_shot, search_tree)
            if current_shot == search_tree:
                print("The BFS failed to find a shot of that type...")
            
            # now check if the shot succeeded
            chance_of_making_the_shot = randint(0, RAND_VAL_RESOLUTION) / RAND_VAL_RESOLUTION
            if chance_of_making_the_shot > current_shot.error_prob:
                # yay you made the shot, now check if it was a winner
                chance_of_winner = randint(0, RAND_VAL_RESOLUTION) / RAND_VAL_RESOLUTION
                if chance_of_winner < current_shot.winner_prob:
                    # yay you hit a winner
                    point_finished = True
                    if next == 1:
                        p1_score += 1
                    else:
                        p2_score += 1
                # if you did not hit a winner and did not miss it, then the point just continues
            else:
                # oh no, you missed it
                point_finished = True
                if next == 1:
                    p2_score += 1
                else:
                    p1_score += 1
            
            next *= -1
            

        score = (p1_score, p2_score)
        side *= -1 # switch sides
        if p1_score + p2_score == 1:
            server *= -1 # switch server if it was the first point
        elif (p1_score + p2_score - 1) % 2 == 0:
            server *= -1
    
    print("Final Score:")
    print(score[0], "-", score[1])
    if score[0] > score[1]:
        print("Player 1 wins!")
    else:
        print("Player 2 wins!")