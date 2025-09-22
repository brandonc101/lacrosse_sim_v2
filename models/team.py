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

    def get_goalie(self):
        """Get the team's goalie"""
        for player in self.players:
            if player.position == "Goalie":
                return player
        return None

    def get_players_by_position(self, position: str):
        """Get all players of a specific position"""
        return [player for player in self.players if player.position == position]

    def reset_stats(self):
        """Reset all team and player stats"""
        self.wins = 0
        self.losses = 0
        self.overtime_losses = 0
        self.goals_for = 0
        self.goals_against = 0

        for player in self.players:
            # Reset existing stats
            player.goals = 0
            player.assists = 0
            player.saves = 0
            player.player_of_match = 0

            # Reset NEW stats
            player.games_played = 0
            if player.position == "Goalie":
                player.goals_against = 0
                player.minutes_played = 0

            # Reset match stats
            player.reset_match_stats()
