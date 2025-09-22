import json
import os
from datetime import datetime
from tkinter import messagebox, filedialog

class DataManager:
    """Handles saving and loading league data"""

    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.save_directory = "saves"
        self.ensure_save_directory()

    def ensure_save_directory(self):
        """Create saves directory if it doesn't exist"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

    def player_to_dict(self, player):
        """Convert player object to dictionary for saving"""
        data = {
            'name': player.name,
            'position': player.position,
            'shooting': player.shooting,
            'passing': player.passing,
            'defense': player.defense,
            'stamina': player.stamina,
            'goals': player.goals,
            'assists': player.assists,
            'saves': player.saves,
            'player_of_match': player.player_of_match,
            'games_played': player.games_played,
        }

        # Add goalie-specific stats
        if player.position == "Goalie":
            data['goals_against'] = getattr(player, 'goals_against', 0)
            data['minutes_played'] = getattr(player, 'minutes_played', 0)

        return data

    def dict_to_player(self, data):
        """Create player object from dictionary data"""
        from models.player import Player

        player = Player(
            data['name'],
            data['position'],
            data['shooting'],
            data['passing'],
            data['defense'],
            data['stamina']
        )

        # Load stats
        player.goals = data.get('goals', 0)
        player.assists = data.get('assists', 0)
        player.saves = data.get('saves', 0)
        player.player_of_match = data.get('player_of_match', 0)
        player.games_played = data.get('games_played', 0)

        # Load goalie-specific stats
        if player.position == "Goalie":
            player.goals_against = data.get('goals_against', 0)
            player.minutes_played = data.get('minutes_played', 0)

        return player

    def team_to_dict(self, team):
        """Convert team object to dictionary for saving"""
        return {
            'name': team.name,
            'wins': team.wins,
            'losses': team.losses,
            'overtime_losses': getattr(team, 'overtime_losses', 0),
            'goals_for': team.goals_for,
            'goals_against': team.goals_against,
            'players': [self.player_to_dict(player) for player in team.players]
        }

    def dict_to_team(self, data):
        """Create team object from dictionary data"""
        from models.team import Team

        # Create players first
        players = [self.dict_to_player(player_data) for player_data in data['players']]

        # Create team
        team = Team(data['name'], players)
        team.wins = data.get('wins', 0)
        team.losses = data.get('losses', 0)
        team.overtime_losses = data.get('overtime_losses', 0)
        team.goals_for = data.get('goals_for', 0)
        team.goals_against = data.get('goals_against', 0)

        return team

    def save_league_data(self, filename=None):
        """Save all league data to a JSON file"""
        try:
            if filename is None:
                # Generate default filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"league_save_{timestamp}.json"

            filepath = os.path.join(self.save_directory, filename)

            save_data = {
                'metadata': {
                    'save_date': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'league_info': {
                    'teams_names': self.main_gui.teams_names,
                    'divisions': self.main_gui.divisions,
                    'current_week': getattr(self.main_gui, 'current_week', 0),
                    'season_complete': getattr(self.main_gui, 'season_complete', False)
                },
                'teams': [self.team_to_dict(team) for team in self.main_gui.teams],
                'standings': getattr(self.main_gui, 'standings', {}),
                'schedule': getattr(self.main_gui, 'schedule', []),
                'playoff_schedule': getattr(self.main_gui, 'playoff_schedule', [])
            }

            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)

            messagebox.showinfo("Save Successful", f"League data saved to {filename}")
            return filepath

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save league data: {str(e)}")
            return None

    def load_league_data(self, filepath=None):
        """Load league data from a JSON file"""
        try:
            if filepath is None:
                # Let user choose file
                filepath = filedialog.askopenfilename(
                    title="Load League Data",
                    initialdir=self.save_directory,
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )

                if not filepath:
                    return False  # User cancelled

            with open(filepath, 'r') as f:
                save_data = json.load(f)

            # Load league info
            league_info = save_data.get('league_info', {})
            self.main_gui.teams_names = league_info.get('teams_names', [])
            self.main_gui.divisions = league_info.get('divisions', {})
            self.main_gui.current_week = league_info.get('current_week', 0)
            self.main_gui.season_complete = league_info.get('season_complete', False)

            # Load teams
            teams_data = save_data.get('teams', [])
            self.main_gui.teams = [self.dict_to_team(team_data) for team_data in teams_data]

            # Load other data
            self.main_gui.standings = save_data.get('standings', {})
            self.main_gui.schedule = save_data.get('schedule', [])
            self.main_gui.playoff_schedule = save_data.get('playoff_schedule', [])

            # Update GUI displays
            self.refresh_gui_displays()

            messagebox.showinfo("Load Successful", f"League data loaded from {os.path.basename(filepath)}")
            return True

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load league data: {str(e)}")
            return False

    def refresh_gui_displays(self):
        """Refresh all GUI displays after loading data"""
        # Update status
        if hasattr(self.main_gui, 'status_var'):
            week_text = f"Week {self.main_gui.current_week}"
            if self.main_gui.season_complete:
                week_text += " (Season Complete)"
            self.main_gui.status_var.set(f"League data loaded - {week_text}")

        # Update simulation tab if it exists
        if hasattr(self.main_gui, 'simulation_tab'):
            if hasattr(self.main_gui.simulation_tab, 'week_label'):
                self.main_gui.simulation_tab.week_label.config(
                    text=f"Current Week: {self.main_gui.current_week}"
                )
            if hasattr(self.main_gui.simulation_tab, 'season_progress'):
                self.main_gui.simulation_tab.season_progress['value'] = self.main_gui.current_week

        # Update stats tab
        if hasattr(self.main_gui, 'stats_tab'):
            self.main_gui.stats_tab.update_display()

        # Update standings tab
        if hasattr(self.main_gui, 'standings_tab'):
            self.main_gui.standings_tab.update_display()

        # Update schedule tab
        if hasattr(self.main_gui, 'schedule_tab'):
            self.main_gui.schedule_tab.update_display()

    def auto_save(self):
        """Automatically save league data"""
        filename = "auto_save.json"
        return self.save_league_data(filename)

    def get_save_files(self):
        """Get list of available save files"""
        try:
            files = []
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.save_directory, filename)
                    modified_time = os.path.getmtime(filepath)
                    files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'modified': datetime.fromtimestamp(modified_time)
                    })

            # Sort by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files

        except Exception as e:
            print(f"Error getting save files: {e}")
            return []

# Add these methods to your main GUI class:

def add_save_load_to_main_gui():
    """
    Add these methods to your main GUI class (probably in main.py or gui.py)
    """

    def __init__(self):
        # ... your existing init code ...
        self.data_manager = DataManager(self)

        # Auto-save every 5 minutes (optional)
        self.auto_save_interval = 300000  # 5 minutes in milliseconds
        self.after(self.auto_save_interval, self.auto_save_loop)

    def save_league(self):
        """Menu/button callback to save league data"""
        return self.data_manager.save_league_data()

    def load_league(self):
        """Menu/button callback to load league data"""
        return self.data_manager.load_league_data()

    def auto_save_loop(self):
        """Auto-save loop (optional)"""
        if hasattr(self, 'teams') and self.teams:
            self.data_manager.auto_save()

        # Schedule next auto-save
        self.after(self.auto_save_interval, self.auto_save_loop)

    def add_save_load_menu(self):
        """Add save/load options to your menu bar"""
        # Add this to your menu creation code
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="Save League", command=self.save_league)
        file_menu.add_command(label="Load League", command=self.load_league)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
