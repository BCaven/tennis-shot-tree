"""
    Collection of algorithms that use the tree to decide what shot to hit

    Algorithms:
        Static shot selection: minmax algorithm that tries to maximize chance that you win the point
        Error avoidance: minmax algorithm that chooses the 'safest' path (path with smallest chance of mistake)


    Available statistics:
        num_hit
        num_success
        continue_prob
        winner_prob
        error_prob        
        
"""
from tree import Shot

def max_stat(stat: str, shot: Shot, head: Shot) -> Shot:
    """
        Maximize the desired stat
    
    """
    if not shot.next_shots:
        shot = breadth_first_search(shot.shot, head)


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
    if not shot.next_shots:
        shot = breadth_first_search(shot.shot, head)

    next_shot = shot.next_shots[0]
    min = next_shot.get_stat(stat)
    for next in shot.next_shots:
        if next.get_stat(stat) < min:
            min = next.get_stat(stat)
            next_shot = next
    return next_shot

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
    return tree # if we couldnt find one, just return the head of the tree
                # this should never happen

def human_vs_alg(search_tree: Shot, algorithm, max_score=10):
    """
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
    server = 1 # 1 is p1, -1 is p2

    while score[0] < max_score and score[1] < max_score:
        pass