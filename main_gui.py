import tkinter as tk
from tkinter import ttk

from gui.menu_manager import MenuManager
from gui.tab_manager import TabManager
from config.league_config import LeagueConfig
from utils.game_simulation import GameSimulator
from data_manager import DataManager

class LacrosseSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lacrosse Simulation Manager")
        self.root.geometry("1200x800")

        # Initialize configuration
        self.config = LeagueConfig()
        self._initialize_game_state()

        # Initialize managers
        self.menu_manager = MenuManager(self)
        self.tab_manager = TabManager(self)
        self.game_simulator = GameSimulator(self)
        self.data_manager = DataManager(self)

        # Setup UI
        self._setup_ui()
        self._initialize_game()

    def _initialize_game_state(self):
        """Initialize game state variables"""
        self.current_week = 0
        self.season_complete = False
        self.teams = []
        self.schedule = []
        self.standings = {}
        self.playoff_teams = []
        self.playoff_schedule = []
        self.conference_standings = {}

        # Copy config data for easy access
        self.teams_names = self.config.teams_names
        self.conferences = self.config.conferences
        self.divisions = self.config.divisions
        self.regular_season_weeks = self.config.regular_season_weeks
        self.playoff_weeks = self.config.playoff_weeks
        self.total_season_weeks = self.config.total_season_weeks

    def _setup_ui(self):
        """Setup the main UI"""
        self.menu_manager.setup_menu()
        self.tab_manager.setup_tabs()
        self._create_status_bar()

    def _create_status_bar(self):
        """Create status bar at bottom"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Click 'Simulate Next Week' to begin")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _initialize_game(self):
        """Initialize the game"""
        from lacrosse_names import initialize_rosters_for_teams
        initialize_rosters_for_teams(self.teams_names)
        self.teams = self.game_simulator.create_teams(self.teams_names)
        self.schedule = self.game_simulator.generate_schedule()
        self.game_simulator.initialize_standings()
        self.update_all_displays()
        self.status_var.set("Season initialized - Ready to simulate!")

    def update_all_displays(self):
        """Update all tab displays"""
        self.tab_manager.update_all_displays()

    # Conference/Division helper methods
    def get_team_conference(self, team_name):
        return self.config.get_team_conference(team_name)

    def get_team_division(self, team_name):
        return self.config.get_team_division(team_name)

    def get_team_full_division(self, team_name):
        return self.config.get_team_full_division(team_name)

    def get_conference_teams(self, conference):
        return self.config.get_conference_teams(conference)

    def get_division_teams(self, conference, division):
        return self.config.get_division_teams(conference, division)

def main():
    root = tk.Tk()
    app = LacrosseSimGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
