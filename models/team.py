from typing import List
from models.player import Player

class Team:
    def __init__(self, name: str, players: List[Player]):
        self.name = name
        self.players = players

        # Team record stats
        self.wins = 0
        self.losses = 0
        self.overtime_losses = 0  # New stat

        self.goals_for = 0
        self.goals_against = 0
        
    def points(self) -> int:
        return self.wins * 2 + self.overtime_losses

    def reset_stats(self):
        self.wins = 0
        self.losses = 0
        self.overtime_losses = 0
        self.goals_for = 0
        self.goals_against = 0
        for player in self.players:
            player.goals = 0
            player.assists = 0
            player.saves = 0
            player.player_of_match = 0
            player.reset_match_stats()
