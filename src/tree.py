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
        cleaned_shot = raw_shot #.strip(good_endings + bad_endings)
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
        next_shot = shots.pop(0)
        try:
            # the next shot is already one of the next shots
            index = [s.shot for s in self.next_shots].index(next_shot)
            #print("shot", next_shot, "found at index", index)
            new_shot = self.next_shots[index].update(Shot.from_str(next_shot))
            new_shot.add_point(shots)
        except ValueError:
            # the next shot is new, it has not been seen here before
            #print("shot", next_shot, "has not been seen before")
            new_shot = Shot.from_str(next_shot)
            self.next_shots.append(new_shot)
            new_shot.add_point(shots)




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
    tree_head = Shot("Start", 1, 1, [])
    for point in raw_data:
        tree_head.add_point(parse_individual_point(point))
    return tree_head