class Player:
    def __init__(self, name: str, position: str,
                 shooting: int, passing: int, defense: int, stamina: int):
        self.name = name
        self.position = position  # e.g., "Attacker", "Midfielder", "Defenseman", "Goalie"

        self.shooting = shooting
        self.passing = passing
        self.defense = defense
        self.stamina = stamina

        # Cumulative season stats
        self.goals = 0
        self.assists = 0
        self.saves = 0
        self.player_of_match = 0

        # Per-match stats (reset before each match)
        self.goals_match = 0
        self.assists_match = 0
        self.saves_match = 0

    def reset_match_stats(self):
        self.goals_match = 0
        self.assists_match = 0
        self.saves_match = 0
