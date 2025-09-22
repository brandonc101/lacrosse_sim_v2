import random
from models.player import Player
from models.team import Team
from lacrosse_names import roster_manager

class TeamManager:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def create_teams(self, team_names):
        """Create teams with players"""
        teams = []
        for name in team_names:
            team = Team(name=name, players=self.create_players(name))
            self._initialize_team_stats(team)
            teams.append(team)
        return teams

    def create_players(self, team_name):
        """Create players using realistic names from the roster manager"""
        players = []
        roster_data = roster_manager.get_team_roster(team_name)

        if not roster_data:
            print(f"Warning: No roster found for {team_name}, creating fallback roster")
            return self._create_fallback_roster(team_name)

        for player_data in roster_data:
            player = self._create_player_from_data(player_data)
            self._initialize_player_stats(player)
            players.append(player)

        return players

    def _create_fallback_roster(self, team_name):
        """Create fallback roster if no roster data found"""
        positions = ['Attack'] * 4 + ['Midfield'] * 4 + ['Defense'] * 4 + ['Goalie'] * 2
        players = []

        for i, pos in enumerate(positions):
            player = Player(
                name=f"{team_name} Player{i+1}",
                position=pos,
                shooting=70 + (i * 2) % 30,
                passing=65 + (i * 3) % 25,
                defense=50 + (i * 4) % 40,
                stamina=60 + (i * 5) % 40,
            )
            self._initialize_player_stats(player)
            players.append(player)
        return players

    def _create_player_from_data(self, player_data):
        """Create player from roster data"""
        position = player_data['position']
        stat_ranges = self._get_position_stat_ranges(position)

        shooting = random.randint(*stat_ranges["shooting"])
        passing = random.randint(*stat_ranges["passing"])
        defense = random.randint(*stat_ranges["defense"])
        stamina = random.randint(*stat_ranges["stamina"])

        return Player(
            name=player_data['name'],
            position=position,
            shooting=shooting,
            passing=passing,
            defense=defense,
            stamina=stamina,
        )

    def _get_position_stat_ranges(self, position):
        """Get realistic stat ranges based on position"""
        ranges = {
            "Attack": {"shooting": (70, 95), "passing": (60, 85), "defense": (40, 65), "stamina": (70, 90)},
            "Midfield": {"shooting": (60, 85), "passing": (70, 95), "defense": (50, 75), "stamina": (75, 95)},
            "Defense": {"shooting": (40, 65), "passing": (50, 70), "defense": (80, 95), "stamina": (65, 85)},
            "Goalie": {"shooting": (10, 30), "passing": (40, 60), "defense": (85, 95), "stamina": (60, 80)}
        }
        return ranges.get(position, {"shooting": (50, 80), "passing": (50, 80), "defense": (50, 80), "stamina": (50, 80)})

    def _initialize_team_stats(self, team):
        """Initialize team stats"""
        team.goals_for = 0
        team.goals_against = 0
        team.wins = 0
        team.losses = 0
        team.overtime_losses = 0
        team.points = 0

    def _initialize_player_stats(self, player):
        """Initialize player statistics"""
        player.goals = 0
        player.assists = 0
        player.saves = 0
        player.goals_match = 0
        player.assists_match = 0
        player.saves_match = 0
        player.games_played = 0

        if player.position == "Goalie":
            player.goals_against = 0
            player.minutes_played = 0
            player.goals_against_match = 0
