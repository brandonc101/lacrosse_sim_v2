import random
from models.player import Player
from models.team import Team
from models.match import simulate_match  # Use your advanced match simulation
from lacrosse_names import roster_manager
from utils.playoff_system import PlayoffSystem

class GameSimulator:
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.playoff_system = PlayoffSystem(self.main_gui)

    def create_teams(self, team_names):
        """Create teams with players"""
        teams = []
        for name in team_names:
            team = Team(name=name, players=self.create_players(name))
            # Initialize team stats that your match.py expects
            team.goals_for = 0
            team.goals_against = 0
            team.wins = 0
            team.losses = 0
            team.overtime_losses = 0
            team.points = 0
            teams.append(team)
        return teams

    def create_players(self, team_name):
        """Create 25 players using realistic names from the roster manager"""
        players = []
        roster_data = roster_manager.get_team_roster(team_name)

        if not roster_data:
            print(f"Warning: No roster found for {team_name}, creating fallback roster")
            positions = ['Attack', 'Attack', 'Attack', 'Midfield', 'Midfield', 'Midfield',
                        'Defense', 'Defense', 'Defense', 'Goalie']
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

        for i, player_data in enumerate(roster_data):
            position = player_data['position']
            stat_ranges = self._get_position_stat_ranges(position)

            # Use the realistic ranges instead of random generation
            shooting = random.randint(*stat_ranges["shooting"])
            passing = random.randint(*stat_ranges["passing"])
            defense = random.randint(*stat_ranges["defense"])
            stamina = random.randint(*stat_ranges["stamina"])

            player = Player(
                name=player_data['name'],
                position=position,
                shooting=shooting,
                passing=passing,
                defense=defense,
                stamina=stamina,
            )

            self._initialize_player_stats(player)
            players.append(player)

        return players
    def _get_position_stat_ranges(self, position):
        """Get realistic stat ranges based on position"""
        ranges = {
            "Attack": {
                "shooting": (70, 95), "passing": (60, 85),
                "defense": (40, 65), "stamina": (70, 90)
            },
            "Midfield": {
                "shooting": (60, 85), "passing": (70, 95),
                "defense": (50, 75), "stamina": (75, 95)
            },
            "Defense": {
                "shooting": (40, 65), "passing": (50, 70),
                "defense": (80, 95), "stamina": (65, 85)
            },
            "Goalie": {
                "shooting": (10, 30), "passing": (40, 60),
                "defense": (85, 95), "stamina": (60, 80)
            }
        }
        return ranges.get(position, {
            "shooting": (50, 80), "passing": (50, 80),
            "defense": (50, 80), "stamina": (50, 80)
        })

    def _initialize_player_stats(self, player):
        """Initialize player statistics that match.py expects"""
        # Existing stats
        player.goals = 0
        player.assists = 0
        player.saves = 0
        player.goals_match = 0
        player.assists_match = 0
        player.saves_match = 0

        # NEW: Initialize new tracking stats
        player.games_played = 0

        # Goalie-specific stats
        if player.position == "Goalie":
            player.goals_against = 0
            player.minutes_played = 0
            player.goals_against_match = 0

    def generate_schedule(self):
        """Generate schedule using the advanced scheduling system"""
        try:
            from models.schedule import build_season_schedule

            # Create team objects with divisions for the scheduler
            temp_teams = []
            for team_name in self.main_gui.teams_names:
                team_obj = type('Team', (), {
                    'name': team_name,
                    'division': self.get_team_division(team_name)
                })()
                temp_teams.append(team_obj)

            schedule_data = build_season_schedule(temp_teams)
            return self.convert_advanced_schedule_format(schedule_data)

        except ImportError:
            # Fallback to the basic game_schedule.py
            from game_schedule import generate_schedule
            raw_schedule = generate_schedule(self.main_gui.teams_names, self.main_gui.divisions)
            return self.convert_schedule_format(raw_schedule)

    def convert_advanced_schedule_format(self, schedule_data):
        """Convert the advanced schedule format to GUI format"""
        converted_schedule = []

        for game_data in schedule_data:
            converted_schedule.append({
                'week': game_data['week'],
                'date': game_data['date'],
                'home_team': game_data['home'],
                'away_team': game_data['away'],
                'home_score': None,
                'away_score': None,
                'completed': False
            })

        return converted_schedule

    def convert_schedule_format(self, raw_schedule):
        """Convert basic schedule format to GUI-friendly format"""
        converted_schedule = []
        for week_num, week_games in enumerate(raw_schedule, 1):
            for home_team, away_team in week_games:
                converted_schedule.append({
                    'week': week_num,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': None,
                    'away_score': None,
                    'completed': False
                })
        return converted_schedule

    def initialize_standings(self):
        """Initialize standings for all teams"""
        self.main_gui.standings = {}
        for team_name in self.main_gui.teams_names:
            self.main_gui.standings[team_name] = {
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0,
                "games_played": 0,
                "overtime_losses": 0,
                "division": self.get_team_division(team_name)
            }

    def get_team_division(self, team_name):
        """Get the division for a team"""
        for div_name, teams in self.main_gui.divisions.items():
            if team_name in teams:
                return div_name
        return "Unknown"

    def simulate_next_week(self):
        """Simulate the next week of games including playoffs"""
        if self.main_gui.season_complete:
            return None

        self.main_gui.current_week += 1

        # Handle different phases of the season
        if self.main_gui.current_week <= 13:
            # Regular season
            return self._simulate_regular_season_week()
        elif self.main_gui.current_week <= 16:
            # Playoffs
            return self._simulate_playoff_week()
        else:
            # Offseason (weeks 17-18)
            return self._simulate_offseason_week()

    def _simulate_regular_season_week(self):
        """Simulate a regular season week"""
        week_games = [game for game in self.main_gui.schedule
                     if game.get('week') == self.main_gui.current_week]

        if not week_games:
            # End of regular season, generate playoffs
            self.main_gui.playoff_schedule = self.playoff_system.generate_playoff_schedule()
            return f"Regular season complete! Playoff bracket generated.\n{self._get_playoff_bracket_text()}"

        return self._simulate_games(week_games, "Regular Season")

    def _simulate_playoff_week(self):
        """Simulate a playoff week"""
        if not hasattr(self.main_gui, 'playoff_schedule') or not self.main_gui.playoff_schedule:
            self.main_gui.playoff_schedule = self.playoff_system.generate_playoff_schedule()

        week_games = [game for game in self.main_gui.playoff_schedule
                     if game.get('week') == self.main_gui.current_week]

        if not week_games:
            if self.main_gui.current_week == 16:
                self.main_gui.season_complete = True
                return "Championship complete! Season finished."
            return f"No playoff games scheduled for week {self.main_gui.current_week}"

        results = self._simulate_games(week_games, "Playoffs")

        # Update playoff bracket for next week
        self.playoff_system.update_playoff_bracket(self.main_gui.current_week)

        return results

    def _simulate_offseason_week(self):
        """Handle offseason weeks"""
        if self.main_gui.current_week == 17:
            return "Week 17: Offseason begins. Draft preparation in progress..."
        elif self.main_gui.current_week == 18:
            return "Week 18: Draft week. New players entering the league..."
        else:
            self.main_gui.season_complete = True
            return "Season cycle complete."

    def _simulate_games(self, week_games, phase_name):
        """Simulate a list of games"""
        results_text = f"Week {self.main_gui.current_week} {phase_name} Results:\n" + "="*50 + "\n"

        for game in week_games:
            home_team_name = game['home_team']
            away_team_name = game['away_team']

            # Skip TBD games
            if "TBD" in home_team_name or "TBD" in away_team_name:
                results_text += f"{game.get('round', 'Game')}: {away_team_name} @ {home_team_name}\n"
                continue

            home_team = None
            away_team = None
            for team in self.main_gui.teams:
                if team.name == home_team_name:
                    home_team = team
                elif team.name == away_team_name:
                    away_team = team

            if home_team and away_team:
                match_result = simulate_match(home_team, away_team)

                game["home_score"] = match_result.home_score
                game["away_score"] = match_result.away_score
                game["completed"] = True

                if self.main_gui.current_week <= 13:
                    # Only update standings during regular season
                    self._update_standings_from_match(home_team, away_team, match_result)

                overtime_text = " (OT)" if match_result.overtime else ""
                winner = home_team_name if match_result.home_score > match_result.away_score else away_team_name

                round_text = game.get('round', '')
                if round_text:
                    results_text += f"{round_text}: "

                results_text += f"{away_team_name} @ {home_team_name}: {match_result.away_score}-{match_result.home_score}{overtime_text} (Winner: {winner})\n"
                results_text += f"  Shots: {home_team_name} {match_result.home_shots}, {away_team_name} {match_result.away_shots}\n"

        status_text = f"Week {self.main_gui.current_week} {phase_name.lower()} simulated successfully"
        if self.main_gui.current_week > 13:
            status_text += f" - {phase_name}"

        self.main_gui.status_var.set(status_text)
        return results_text

    def _get_playoff_bracket_text(self):
        """Generate text representation of playoff bracket"""
        playoff_teams = self.playoff_system.determine_playoff_teams()

        eastern_teams = [t for t in playoff_teams if self.playoff_system.get_conference_from_division(t['division']) == 'Eastern']
        western_teams = [t for t in playoff_teams if self.playoff_system.get_conference_from_division(t['division']) == 'Western']

        eastern_teams.sort(key=lambda x: (x['win_pct'], x['point_diff']), reverse=True)
        western_teams.sort(key=lambda x: (x['win_pct'], x['point_diff']), reverse=True)

        bracket_text = "\nPLAYOFF BRACKET:\n"
        bracket_text += "Eastern Conference:\n"
        for i, team in enumerate(eastern_teams, 1):
            bracket_text += f"  {i}. {team['name']} ({team['wins']}-{team['losses']})\n"

        bracket_text += "\nWestern Conference:\n"
        for i, team in enumerate(western_teams, 1):
            bracket_text += f"  {i}. {team['name']} ({team['wins']}-{team['losses']})\n"

        return bracket_text

    def _update_standings_from_match(self, home_team, away_team, match_result):
        """Update standings using the advanced team stats from match.py"""
        home_name = home_team.name
        away_name = away_team.name

        if home_name in self.main_gui.standings:
            self.main_gui.standings[home_name]["wins"] = home_team.wins
            self.main_gui.standings[home_name]["losses"] = home_team.losses + home_team.overtime_losses
            self.main_gui.standings[home_name]["points_for"] = home_team.goals_for
            self.main_gui.standings[home_name]["points_against"] = home_team.goals_against
            self.main_gui.standings[home_name]["games_played"] = home_team.wins + home_team.losses + home_team.overtime_losses
            self.main_gui.standings[home_name]["overtime_losses"] = home_team.overtime_losses

        if away_name in self.main_gui.standings:
            self.main_gui.standings[away_name]["wins"] = away_team.wins
            self.main_gui.standings[away_name]["losses"] = away_team.losses + away_team.overtime_losses
            self.main_gui.standings[away_name]["points_for"] = away_team.goals_for
            self.main_gui.standings[away_name]["points_against"] = away_team.goals_against
            self.main_gui.standings[away_name]["games_played"] = away_team.wins + away_team.losses + away_team.overtime_losses
            self.main_gui.standings[away_name]["overtime_losses"] = away_team.overtime_losses

    def simulate_entire_season(self):
        """Simulate the entire remaining season"""
        max_weeks = 50
        week_count = 0

        while not self.main_gui.season_complete and week_count < max_weeks:
            old_week = self.main_gui.current_week
            self.simulate_next_week()
            if self.main_gui.current_week == old_week:
                break
            week_count += 1

        return week_count

    def reset_season(self):
        """Reset the season to the beginning"""
        self.main_gui.current_week = 0
        self.main_gui.season_complete = False
        self.main_gui.teams = self.create_teams(self.main_gui.teams_names)
        self.main_gui.schedule = self.generate_schedule()
        self.initialize_standings()
        self.main_gui.status_var.set("Season reset - Click 'Simulate Next Week' to begin")

    def get_save_data(self):
        """Get data to save"""
        return {
            "current_week": self.main_gui.current_week,
            "season_complete": self.main_gui.season_complete,
            "standings": self.main_gui.standings,
            "schedule": self.main_gui.schedule
        }

    def load_save_data(self, save_data):
        """Load saved data"""
        self.main_gui.current_week = save_data["current_week"]
        self.main_gui.season_complete = save_data["season_complete"]
        self.main_gui.standings = save_data["standings"]

        if hasattr(self.main_gui, 'simulation_tab'):
            self.main_gui.simulation_tab.week_label.config(text=f"Current Week: {self.main_gui.current_week}")
            self.main_gui.simulation_tab.season_progress['value'] = self.main_gui.current_week
