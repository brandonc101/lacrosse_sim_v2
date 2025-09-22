from utils.team_manager import TeamManager
from utils.schedule_manager import ScheduleManager
from utils.season_simulator import SeasonSimulator
from utils.playoff_system import PlayoffSystem

class GameSimulator:
    def __init__(self, main_gui):
        self.main_gui = main_gui

        # Initialize specialized managers
        self.team_manager = TeamManager(main_gui)
        self.schedule_manager = ScheduleManager(main_gui)
        self.season_simulator = SeasonSimulator(main_gui)
        self.playoff_system = PlayoffSystem(main_gui)

    def create_teams(self, team_names):
        """Delegate to team manager"""
        return self.team_manager.create_teams(team_names)

    def generate_schedule(self):
        """Delegate to schedule manager"""
        return self.schedule_manager.generate_schedule()

    def simulate_next_week(self):
        """Delegate to season simulator"""
        return self.season_simulator.simulate_next_week()

    def simulate_entire_season(self):
        """Delegate to season simulator"""
        return self.season_simulator.simulate_entire_season()

    def reset_season(self):
        """Reset all components"""
        self.main_gui.current_week = 0
        self.main_gui.season_complete = False
        self.main_gui.teams = self.team_manager.create_teams(self.main_gui.teams_names)
        self.main_gui.schedule = self.schedule_manager.generate_schedule()
        self.initialize_standings()
        self.main_gui.status_var.set("Season reset - Click 'Simulate Next Week' to begin")

    def initialize_standings(self):
        """Initialize standings for all teams"""
        self.main_gui.standings = {}
        for team_name in self.main_gui.teams_names:
            self.main_gui.standings[team_name] = {
                "wins": 0, "losses": 0, "points_for": 0, "points_against": 0,
                "games_played": 0, "overtime_losses": 0,
                "division": self.get_team_division(team_name)
            }

    def get_team_division(self, team_name):
        """Get the division for a team"""
        for div_name, teams in self.main_gui.divisions.items():
            if team_name in teams:
                return div_name
        return "Unknown"

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
