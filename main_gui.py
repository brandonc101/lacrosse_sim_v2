import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Import your existing modules
from lacrosse_names import initialize_rosters_for_teams

# Import the new tab modules
from tabs.simulation_tab import SimulationTab
from tabs.standings_tab import StandingsTab
from tabs.schedule_tab import ScheduleTab
from tabs.roster_tab import RosterTab
from tabs.stats_tab import StatsTab

# Import utilities
from utils.game_simulation import GameSimulator
from data_manager import DataManager

class LacrosseSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lacrosse Simulation Manager")
        self.root.geometry("1200x800")

        # Game state variables
        self.current_week = 0
        self.season_complete = False
        self.teams = []
        self.schedule = []
        self.standings = {}

        # Team names organized by conference and division
        self.teams_names = [
            "Buffalo Glacier", "Richmond Rebellion", "Louisville Stampede",
            "Minneapolis Chill", "Phoenix Dustrunners", "San Jose Quakebirds",
            "Toronto Ironhawks", "Montreal Sentries", "Calgary Nightwolves",
            "Spokane Tempest", "El Paso Vortex", "Atlanta Firewing"
        ]

        # Conference and division structure
        self.conferences = {
            "Eastern": {
                "North": ["Buffalo Glacier", "Toronto Ironhawks", "Montreal Sentries"],
                "South": ["Richmond Rebellion", "Louisville Stampede", "Atlanta Firewing"]
            },
            "Western": {
                "North": ["Minneapolis Chill", "Calgary Nightwolves", "Spokane Tempest"],
                "South": ["San Jose Quakebirds", "Phoenix Dustrunners", "El Paso Vortex"]
            }
        }

        # Flat divisions for compatibility with existing code
        self.divisions = {
            "Eastern North": self.conferences["Eastern"]["North"],
            "Eastern South": self.conferences["Eastern"]["South"],
            "Western North": self.conferences["Western"]["North"],
            "Western South": self.conferences["Western"]["South"]
        }

        self.regular_season_weeks = 13
        self.playoff_weeks = 3
        self.total_season_weeks = 16
        self.playoff_teams = []
        self.playoff_schedule = []
        self.conference_standings = {}

        # Initialize game simulator
        self.game_simulator = GameSimulator(self)

        # Setup UI first
        self.setup_ui()

        # Initialize game
        self.initialize_game()

        # Initialize data manager AFTER everything else is set up
        self.data_manager = DataManager(self)

    def setup_ui(self):
        # Create main menu bar (FIXED VERSION)
        self.setup_menu()

        # Create main frame with notebook for tabs
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize all tabs
        self.simulation_tab = SimulationTab(self.notebook, self)
        self.standings_tab = StandingsTab(self.notebook, self)
        self.schedule_tab = ScheduleTab(self.notebook, self)
        self.roster_tab = RosterTab(self.notebook, self)
        self.stats_tab = StatsTab(self.notebook, self)

        # Status bar at bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Click 'Simulate Next Week' to begin")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New Season", command=self.new_season)
        file_menu.add_separator()
        file_menu.add_command(label="Save League (New)", command=self.save_league)
        file_menu.add_command(label="Load League (New)", command=self.load_league)
        file_menu.add_separator()
        file_menu.add_command(label="Save Game (Old)", command=self.save_game)
        file_menu.add_command(label="Load Game (Old)", command=self.load_game)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def initialize_game(self):
        """Initialize the game"""
        initialize_rosters_for_teams(self.teams_names)
        self.teams = self.game_simulator.create_teams(self.teams_names)
        self.schedule = self.game_simulator.generate_schedule()
        self.game_simulator.initialize_standings()
        self.update_all_displays()
        self.status_var.set("Season initialized - Ready to simulate!")

    def update_all_displays(self):
        """Update all tab displays"""
        self.standings_tab.update_display()
        self.schedule_tab.update_display()
        self.roster_tab.update_display()
        self.stats_tab.update_display()

    def get_team_conference(self, team_name):
        """Get the conference for a team"""
        for conference, divisions in self.conferences.items():
            for division, teams in divisions.items():
                if team_name in teams:
                    return conference
        return "Unknown"

    def get_team_division(self, team_name):
        """Get the division for a team (returns simple name like 'North' or 'South')"""
        for conference, divisions in self.conferences.items():
            for division, teams in divisions.items():
                if team_name in teams:
                    return division
        return "Unknown"

    def get_team_full_division(self, team_name):
        """Get the full division name for a team (e.g., 'Eastern North')"""
        for div_name, teams in self.divisions.items():
            if team_name in teams:
                return div_name
        return "Unknown"

    def get_conference_teams(self, conference):
        """Get all teams in a conference"""
        if conference in self.conferences:
            teams = []
            for division, team_list in self.conferences[conference].items():
                teams.extend(team_list)
            return teams
        return []

    def get_division_teams(self, conference, division):
        """Get teams in a specific conference division"""
        if conference in self.conferences and division in self.conferences[conference]:
            return self.conferences[conference][division]
        return []

    def new_season(self):
        """Start a new season"""
        self.game_simulator.reset_season()
        messagebox.showinfo("New Season", "New season started!")

    # NEW SAVE/LOAD METHODS (using DataManager)
    def save_league(self):
        """Save current league data using new system"""
        if hasattr(self, 'data_manager'):
            return self.data_manager.save_league_data()
        else:
            messagebox.showerror("Error", "Data manager not initialized")

    def load_league(self):
        """Load league data from file using new system"""
        if hasattr(self, 'data_manager'):
            return self.data_manager.load_league_data()
        else:
            messagebox.showerror("Error", "Data manager not initialized")

    # OLD SAVE/LOAD METHODS (keep for compatibility)
    def save_game(self):
        """Save the current game state (old method)"""
        try:
            save_data = self.game_simulator.get_save_data()
            with open("lacrosse_save.json", "w") as f:
                json.dump(save_data, f, indent=2, default=str)
            messagebox.showinfo("Save Game", "Game saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving game: {str(e)}")

    def load_game(self):
        """Load a saved game state (old method)"""
        try:
            if os.path.exists("lacrosse_save.json"):
                with open("lacrosse_save.json", "r") as f:
                    save_data = json.load(f)
                self.game_simulator.load_save_data(save_data)
                self.update_all_displays()
                messagebox.showinfo("Load Game", "Game loaded successfully!")
            else:
                messagebox.showwarning("Load Game", "No saved game found!")
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading game: {str(e)}")

def main():
    root = tk.Tk()
    app = LacrosseSimGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
