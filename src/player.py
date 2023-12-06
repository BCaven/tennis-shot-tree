class Player:
    """
        Class to store data about the player
    
        Useful for higher-level algorithms that try to target weaknesses of specific players
        while also using a general tree
    """
    def __init__(self, dominant_hand):
        self.dominant_hand = dominant_hand
        self.shots = {}
        self.mistakes = {}
        self.winners = {}

    def add_mistake(self, shot: str):
        """
            Add mistake
        
        """
        try:
            self.mistakes[shot] += 1
        except Exception:
            self.mistakes[shot] = 1
    
    def add_winner(self, shot: str):
        """
            Add winner
        """
        try:
            self.winners[shot] += 1
        except Exception:
            self.winners[shot] = 1
    
    def add_shot(self, shot: str):
        """
            Add a shot
        """
        try:
            self.shots[shot] += 1
        except Exception:
            self.shots[shot] = 1