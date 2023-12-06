"""
Classes and functions that are used to build the shot tree


TODO: implement additional features

ADDITIONAL FEATURES:
    - mistake tracking

"""
import sys

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
    def __init__(self, shot: str, num_times_hit: int, num_times_success: int, next_shots: list, outcomes: dict={}):
        self.shot = shot
        self.num_hit = num_times_hit
        self.num_success = num_times_success
        self.next_shots = next_shots
        self.outcomes = outcomes
        self.continue_prob = 0
        self.winner_prob = 0
        self.error_prob = 0
    
    def usage(return_val):
        print("""
Shot class:
    shot            : str           = name of the shot
    num_hit         : int           = number of times this node happened
    num_success     : int           = number of times this shot was successful
    next_shots      : list[Shot]    = list of shot objects that occurred after this shot was hit
    outcomes        : dict[str]     = dictionary of possible endings for this shot and how many times they occurred
                                      this includes points that continued after the current shot
                                      shot depth is potentially included in the outcome dict
                                      shots that continued but did not specify depth are marked as 'continue'
    continue_prob   : float         = value from 0-1 describing likelyhood of point continuing after this shot
    winner_prob     : float         = value from 0-1 describing likelyhood of this shot being a winner
    error_prob      : float         = value from 0-1 describing likelyhood of this shot being an error

        """)
        sys.exit(return_val)

    @classmethod
    def from_str(cls, raw_shot: str, good_endings="*789", bad_endings="nwdxg!V@#Ce", prefix='c'):
        """
            Build shot object from the raw string
            Assuming the shot is constructed as such:

        """
        # really there are just two things we need here: the shot, and the ending
        # split the shot from the ending, interpret the ending, call it a day
        # if the shot does not HAVE an ending, it was successful
        # split the shot
        
        bad_ending = any(s in bad_endings for s in raw_shot)
        cleaned_shot = raw_shot.strip(good_endings + bad_endings)
        # remove lets c5 -> 5
        for c in prefix:
            cleaned_shot = cleaned_shot.lstrip(c)
        suffix = "".join([c if c in good_endings+bad_endings else "" for c in raw_shot])
        if not suffix:
            suffix = "continue"
        if bad_ending:
            # you just lost the point
            return cls(cleaned_shot, 1, 0, [], {suffix: 1})
        else:
            # you made the shot, but the point is still going
            # or you just won the point
            return cls(cleaned_shot, 1, 1, [], {suffix: 1})

    def get_stat(self, stat: str):
        match stat:
            case "num_hit": return self.num_hit
            case "num_success": return self.num_success
            case "continue_prob": return self.continue_prob
            case "winner_prob": return self.winner_prob
            case "error_prob": return self.error_prob
            case _: Shot.usage(1)

    def update(self, shot, sort=True, rally_continues: list=["7", "8", "9", "continue"]):
        """
            Combine this node's data with another node's data
            returns itself (a.k.a. the updated node)

            TODO: make the `sort` parameter a lambda function so the user can use custom
                  sorting functions
        """
        self.num_hit += shot.num_hit
        for shot in shot.next_shots:
            self.add_next_shot(shot)
        for outcome in shot.outcomes:
            try:
                self.outcomes[outcome] += shot.outcomes[outcome]
            except Exception:
                self.outcomes[outcome] = shot.outcomes[outcome]
        # sort the next_shots, shots that got hit more times are first
        # this is mostly just for usability so more common shots are listed before
        # uncommon shots
        # This is opperating under the assumption that less common shots are less
        # desirable or in some way not as likely (seeing as they got hit fewer times)
        if sort:
            self.next_shots.sort(key=lambda x: x.num_hit, reverse=True)
        
        # update probabilities
        self.num_success = 0
        try:
            continue_sum = 0
            for c in rally_continues:
                if c in self.outcomes:
                    continue_sum += self.outcomes[c]
            self.continue_prob = continue_sum / self.num_hit
            self.num_success += continue_sum
        except Exception:
            self.continue_prob = 0
        try:
            winner_sum = 0
            for key in self.outcomes:
                if '*' in key:
                    winner_sum += self.outcomes[key]
            self.winner_prob = winner_sum / self.num_hit
            self.num_success += winner_sum
        except Exception:
            self.winner_prob = 0
        try:
            error_sum = 0
            for key in self.outcomes:
                if (key not in rally_continues) and ('*' not in key):
                    error_sum += self.outcomes[key]
            self.error_prob = error_sum / self.num_hit
        except Exception:
            self.error_prob = 0
        
        num_outcomes = sum(self.outcomes[s] for s in self.outcomes)
        assert self.num_hit == num_outcomes, "number of times hit does not equal the total number of outcomes seen"
        prob_sum = round(self.continue_prob + self.winner_prob + self.error_prob, 5)
        assert prob_sum == 1, "percentages do not equal the correct value"
        return self
    def add_next_shot(self, next_shot, sort=True, require_direction=True):
        """
            Add a next_shot
        """

        next_shot_indexes = [s.shot for s in self.next_shots]
        if next_shot.shot in next_shot_indexes:
            index = next_shot_indexes.index(next_shot.shot)
            self.next_shots[index].update(next_shot, sort=sort)
        else:
            self.next_shots.append(next_shot)
        
    
    def add_point(self, shots: list, ignored_points="SRPQ0;"):
        """
            Parameter: list describing a point

            Adds that point to the tree

            TODO: ignore shots that do not include direction (i.e. 'b' instead of 'b3')
        
        """
        if not shots:
            return
        raw_next = shots.pop(0).replace(" ", "") # remove spaces
        #raw_next = raw_next.replace("c", "") # remove lets
        if not raw_next:
            return
        next_shot = Shot.from_str(raw_next)
        if any(s in ignored_points for s in next_shot.shot):
            return
        try:
            # the next shot is already one of the next shots
            index = [s.shot for s in self.next_shots].index(next_shot.shot)
            #print("shot", next_shot, "found at index", index)
            new_shot = self.next_shots[index].update(next_shot)
            new_shot.add_point(shots)
        except ValueError:
            # the next shot is new, it has not been seen here before
            #print("shot", next_shot, "has not been seen before")
            self.next_shots.append(next_shot)
            next_shot.add_point(shots)

    def clean_tree(self, max_keep=10, clean_dead=[]):
        """
            Remove directionless shots if versions are present that have direction

            TODO: make this method usable
        """
        # assumption: tree is sorted
        self.next_shots = self.next_shots[:max_keep]
        indexes_to_remove = set()
        for index, shot in enumerate(self.next_shots):
            for item in clean_dead:
                if shot.shot == item:
                    indexes_to_remove.add(index)
            if index not in indexes_to_remove:
                shot.clean_tree(max_keep)
        indexes_to_remove = list(indexes_to_remove)
        indexes_to_remove.sort(reverse=True)
        for i in indexes_to_remove:
            self.next_shots.pop(i)




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

def sort_data(raw_data, valid_starts="456") -> Shot:
    """
        Shot tree starts with a placeholder "start" node
        Each possible serve is contained in head.next_shots
        from there the rally is stored in the tree as expected
    """
    tree_head = Shot("Start", 1, 1, [])
    for point in raw_data:
        individual_points = parse_individual_point(point)
        if not individual_points:
            continue
        if any(c in valid_starts for c in individual_points[0]): # ignoring all points that do not
                                                                 # start with a serve
                                                                 # done primarily to avoid incorrect
                                                                 # optimizations in minmax algorithms
            tree_head.add_point(individual_points)
    return tree_head