class Player:
    def __init__(self, name: str, position: str,
                 shooting: int, passing: int, defense: int, stamina: int):
        self.name = name
        self.position = position  # e.g., "Attack", "Midfield", "Defense", "Goalie"
        self.shooting = shooting
        self.passing = passing
        self.defense = defense
        self.stamina = stamina

        # Cumulative season stats
        self.goals = 0
        self.assists = 0
        self.saves = 0
        self.player_of_match = 0

        # NEW: Additional tracking stats
        self.games_played = 0
        self.goals_against = 0 if position == "Goalie" else None  # Only for goalies
        self.minutes_played = 0 if position == "Goalie" else None  # Only for goalies

        # Per-match stats (reset before each match)
        self.goals_match = 0
        self.assists_match = 0
        self.saves_match = 0
        self.goals_against_match = 0 if position == "Goalie" else None  # NEW: Match goals against

    def reset_match_stats(self):
        """Reset per-match stats before each game"""
        self.goals_match = 0
        self.assists_match = 0
        self.saves_match = 0
        if self.position == "Goalie" and hasattr(self, 'goals_against_match'):
            self.goals_against_match = 0

    def increment_games_played(self):
        """Increment games played counter"""
        self.games_played += 1

    def add_goal_against(self):
        """Add a goal against (goalies only)"""
        if self.position == "Goalie":
            if self.goals_against is not None:
                self.goals_against += 1
            if hasattr(self, 'goals_against_match') and self.goals_against_match is not None:
                self.goals_against_match += 1

    def add_minutes_played(self, minutes):
        """Add minutes played (goalies only)"""
        if self.position == "Goalie" and self.minutes_played is not None:
            self.minutes_played += minutes

    def get_save_percentage(self):
        """Calculate and return save percentage"""
        if self.position != "Goalie" or self.saves == 0:
            return None

        total_shots = self.saves + (self.goals_against or 0)
        if total_shots == 0:
            return 0.0

        return (self.saves / total_shots) * 100

    def get_gaa(self):
        """Calculate and return Goals Against Average"""
        if self.position != "Goalie" or not self.minutes_played or self.minutes_played == 0:
            return None

        # Standard game is 60 minutes
        return ((self.goals_against or 0) * 60) / self.minutes_played

    def add_goal(self):
        """Add a goal to season and match stats"""
        self.goals += 1
        self.goals_match += 1

    def add_assist(self):
        """Add an assist to season and match stats"""
        self.assists += 1
        self.assists_match += 1

    def add_save(self):
        """Add a save to season and match stats"""
        if self.position == "Goalie":
            self.saves += 1
            self.saves_match += 1

    def finalize_match_stats(self):
        """Called at end of match to finalize any calculations"""
        # This can be used for any end-of-match processing if needed
        pass

    def get_overall_rating(self):
        """Calculate overall rating based on position and attributes"""
        if self.position == "Goalie":
            # For goalies, defense is most important
            return int((self.defense * 0.6 + self.stamina * 0.3 + self.passing * 0.1))
        elif self.position == "Attack":
            # For attackers, shooting is most important
            return int((self.shooting * 0.5 + self.passing * 0.3 + self.stamina * 0.2))
        elif self.position == "Midfield":
            # For midfielders, balanced across all skills
            return int((self.passing * 0.4 + self.shooting * 0.2 + self.defense * 0.2 + self.stamina * 0.2))
        elif self.position == "Defense":
            # For defensemen, defense and passing are most important
            return int((self.defense * 0.5 + self.passing * 0.3 + self.stamina * 0.2))
        else:
            # Default calculation
            return int((self.shooting + self.passing + self.defense + self.stamina) / 4)

    def reset_season_stats(self):
        """Reset all season stats to zero"""
        self.goals = 0
        self.assists = 0
        self.saves = 0
        self.player_of_match = 0
        self.games_played = 0

        if self.position == "Goalie":
            self.goals_against = 0
            self.minutes_played = 0

    def __str__(self):
        return f"{self.name} ({self.position}) - Goals: {self.goals}, Assists: {self.assists}, Games: {self.games_played}"

    def __repr__(self):
        return f"Player('{self.name}', '{self.position}', {self.shooting}, {self.passing}, {self.defense}, {self.stamina})"
