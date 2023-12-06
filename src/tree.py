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
    shot: str               = name of the shot
    num_hit: int            = number of times this node happened
    num_success: int        = number of times this shot was successful
    next_shots: list[Shot]  = list of shot objects that occurred after this shot was hit
    outcomes: dict[str]     = dictionary of possible endings for this shot and how many times they occurred
                              this includes points that continued after the current shot
                              shot depth is potentially included in the outcome dict
                              shots that continued but did not specify depth are marked as 'continue'
    continue_prob: float    = value from 0-1 describing likelyhood of point continuing after this shot
    winner_prob: float      = value from 0-1 describing likelyhood of this shot being a winner
    error_prob: float       = value from 0-1 describing likelyhood of this shot being an error

        """)
        sys.exit(return_val)

    @classmethod
    def from_str(cls, raw_shot: str, good_endings="*789", bad_endings="nwdxg!V@#"):
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
        suffix = "".join([c if c in good_endings+bad_endings else "" for c in raw_shot])
        if not suffix:
            suffix = "continue"
        if ending in bad_endings:
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
        """
        self.num_hit += shot.num_hit
        self.num_success += shot.num_success
        for shot in shot.next_shots:
            self.add_next_shot(shot)
        for outcome in shot.outcomes:
            try:
                self.outcomes[outcome] += shot.outcomes[outcome]
            except Exception:
                self.outcomes[outcome] = shot.outcomes[outcome]
        # sort the next_shots
        if sort:
            self.next_shots.sort(key=lambda x: x.num_hit, reverse=True)
        
        # update probabilities
        try:
            for c in rally_continues:
                if c in self.outcomes:
                    self.continue_prob += self.outcomes[c]
            self.continue_prob /= self.num_hit
        except Exception:
            self.continue_prob = 0
        try:
            self.winner_prob = self.outcomes['*'] / self.num_hit
        except Exception:
            self.winner_prob = 0
        try:
            self.error_prob = (self.num_hit - self.num_success) / self.num_hit
        except Exception:
            self.error_prob = 0
        return self
    def add_next_shot(self, next_shot):
        """
            Add a next_shot
        """
        next_shot_indexes = [s.shot for s in self.next_shots]
        if next_shot.shot in next_shot_indexes:
            index = next_shot_indexes.index(next_shot.shot)
            self.next_shots[index].update(next_shot)
        else:
            self.next_shots.append(next_shot)
    
    def add_point(self, shots: list):
        """
            Parameter: string describing a point

            Adds that point to the tree
        
        """
        if not shots:
            return
        next_shot = Shot.from_str(shots.pop(0))
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
        Shot tree starts with a placeholder "start" node
        Each possible serve is contained in head.next_shots
        from there the rally is stored in the tree as expected
    """
    tree_head = Shot("Start", 1, 1, [])
    for point in raw_data:
        tree_head.add_point(parse_individual_point(point))
    return tree_head