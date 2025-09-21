import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
import os
import random

# Import your existing modules
from models.player import Player
from models.team import Team
from game_schedule import generate_schedule
from lacrosse_names import get_player_name_for_team, initialize_rosters_for_teams, roster_manager

# Import season module
try:
    from season import simulate_season
except ImportError:
    simulate_season = None  # Handle if season.py doesn't exist or has issues

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
        self.all_games_results = []

        # Team names and divisions from your main.py
        self.teams_names = [
            "Buffalo Glacier", "Richmond Rebellion", "Louisville Stampede",
            "Minneapolis Chill", "Phoenix Dustrunners", "San Jose Quakebirds",
            "Toronto Ironhawks", "Montreal Sentries", "Calgary Nightwolves",
            "Spokane Tempest", "El Paso Vortex", "Atlanta Firewing"
        ]

        self.divisions = {
            "East North": ["Buffalo Glacier", "Toronto Ironhawks", "Montreal Sentries"],
            "East South": ["Richmond Rebellion", "Louisville Stampede", "Atlanta Firewing"],
            "West North": ["Minneapolis Chill", "Calgary Nightwolves", "Spokane Tempest"],
            "West South": ["San Jose Quakebirds", "Phoenix Dustrunners", "El Paso Vortex"]
        }

        self.setup_ui()
        self.initialize_game()

    def create_players(self, team_name):
        """Create 25 players using realistic names from the roster manager"""
        players = []

        # Get the full roster from the name system (25 players)
        roster_data = roster_manager.get_team_roster(team_name)

        if not roster_data:
            # Fallback if no roster found - create minimal roster
            print(f"Warning: No roster found for {team_name}, creating fallback roster")
            positions = ['Attack', 'Attack', 'Attack', 'Midfield', 'Midfield', 'Midfield',
                        'Defense', 'Defense', 'Defense', 'Goalie']
            for i, pos in enumerate(positions):
                players.append(Player(
                    name=f"{team_name} Player{i+1}",
                    position=pos,
                    shooting=70 + (i * 2) % 30,
                    passing=65 + (i * 3) % 25,
                    defense=50 + (i * 4) % 40,
                    stamina=60 + (i * 5) % 40,
                ))
            return players

        # Create players from the full 25-player roster
        for i, player_data in enumerate(roster_data):
            # Generate varied but realistic stats for each player
            # Base stats with some variation
            base_shooting = random.randint(50, 85)
            base_passing = random.randint(50, 85)
            base_defense = random.randint(50, 85)
            base_stamina = random.randint(55, 90)

            # Position-specific stat adjustments
            position = player_data['position']
            if position == 'Attack':
                base_shooting += random.randint(5, 15)  # Attackers are better shooters
                base_passing += random.randint(0, 10)
            elif position == 'Midfield':
                base_passing += random.randint(5, 15)   # Midfielders are better passers
                base_stamina += random.randint(5, 10)   # More stamina
            elif position == 'Defense':
                base_defense += random.randint(10, 20)  # Defenders are much better at defense
                base_shooting -= random.randint(5, 15)  # Less shooting ability
            elif position == 'Goalie':
                base_defense += random.randint(15, 25)  # Goalies have high defense
                base_shooting -= random.randint(10, 20) # Low shooting
                base_passing -= random.randint(5, 15)   # Lower passing

            # Ensure stats stay within reasonable bounds (30-100)
            shooting = max(30, min(100, base_shooting))
            passing = max(30, min(100, base_passing))
            defense = max(30, min(100, base_defense))
            stamina = max(30, min(100, base_stamina))

            players.append(Player(
                name=player_data['name'],
                position=position,
                shooting=shooting,
                passing=passing,
                defense=defense,
                stamina=stamina,
            ))

        return players

    def setup_ui(self):
        # Create main menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Season", command=self.new_season)
        file_menu.add_command(label="Save Game", command=self.save_game)
        file_menu.add_command(label="Load Game", command=self.load_game)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Create main frame with notebook for tabs
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Setup different tabs
        self.setup_simulation_tab()
        self.setup_standings_tab()
        self.setup_schedule_tab()
        self.setup_roster_tab()
        self.setup_stats_tab()

        # Status bar at bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Click 'Simulate Next Week' to begin")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_simulation_tab(self):
        sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(sim_frame, text="Simulation Control")

        # Week information
        week_info_frame = ttk.LabelFrame(sim_frame, text="Season Progress", padding=10)
        week_info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.week_label = ttk.Label(week_info_frame, text="Current Week: 0", font=("Arial", 12, "bold"))
        self.week_label.pack(pady=5)

        self.season_progress = ttk.Progressbar(week_info_frame, length=400, mode='determinate')
        self.season_progress.pack(pady=5)

        # Control buttons
        button_frame = ttk.Frame(sim_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.sim_week_btn = ttk.Button(button_frame, text="Simulate Next Week",
                                      command=self.simulate_next_week, style="Accent.TButton")
        self.sim_week_btn.pack(side=tk.LEFT, padx=5)

        self.sim_season_btn = ttk.Button(button_frame, text="Simulate Entire Season",
                                       command=self.simulate_entire_season)
        self.sim_season_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(button_frame, text="Reset Season", command=self.reset_season)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Recent games display
        recent_frame = ttk.LabelFrame(sim_frame, text="Recent Games", padding=10)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.recent_games_text = scrolledtext.ScrolledText(recent_frame, height=15, width=80)
        self.recent_games_text.pack(fill=tk.BOTH, expand=True)

    def setup_standings_tab(self):
        standings_frame = ttk.Frame(self.notebook)
        self.notebook.add(standings_frame, text="Standings")

        # Division selector
        div_frame = ttk.Frame(standings_frame)
        div_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(div_frame, text="View Division:").pack(side=tk.LEFT, padx=5)
        self.division_combobox = ttk.Combobox(div_frame, values=["All Divisions"] + list(self.divisions.keys()), width=20)
        self.division_combobox.set("All Divisions")
        self.division_combobox.pack(side=tk.LEFT, padx=5)
        self.division_combobox.bind("<<ComboboxSelected>>", self.update_standings_display)

        # Standings treeview
        columns = ("Division", "Team", "Wins", "Losses", "Win %", "Points For", "Points Against", "Diff")
        self.standings_tree = ttk.Treeview(standings_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.standings_tree.heading(col, text=col)
            if col in ["Division", "Team"]:
                self.standings_tree.column(col, width=120, anchor=tk.W)
            else:
                self.standings_tree.column(col, width=80, anchor=tk.CENTER)

        scrollbar_standings = ttk.Scrollbar(standings_frame, orient=tk.VERTICAL, command=self.standings_tree.yview)
        self.standings_tree.configure(yscrollcommand=scrollbar_standings.set)

        self.standings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar_standings.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_schedule_tab(self):
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="Schedule")

        # Week selector
        week_selector_frame = ttk.Frame(schedule_frame)
        week_selector_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(week_selector_frame, text="Select Week:").pack(side=tk.LEFT, padx=5)
        self.week_combobox = ttk.Combobox(week_selector_frame, values=["All Weeks"] + [f"Week {i}" for i in range(1, 19)], width=15)
        self.week_combobox.set("All Weeks")
        self.week_combobox.pack(side=tk.LEFT, padx=5)
        self.week_combobox.bind("<<ComboboxSelected>>", self.display_week_schedule)

        # Schedule display
        schedule_columns = ("Week", "Home Team", "Away Team", "Score", "Status")
        self.schedule_tree = ttk.Treeview(schedule_frame, columns=schedule_columns, show="headings", height=20)

        for col in schedule_columns:
            self.schedule_tree.heading(col, text=col)
            if col in ["Home Team", "Away Team"]:
                self.schedule_tree.column(col, width=150, anchor=tk.W)
            elif col == "Score":
                self.schedule_tree.column(col, width=120, anchor=tk.CENTER)
            else:
                self.schedule_tree.column(col, width=100, anchor=tk.CENTER)

        scrollbar_schedule = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar_schedule.set)

        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar_schedule.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_roster_tab(self):
        roster_frame = ttk.Frame(self.notebook)
        self.notebook.add(roster_frame, text="Team Roster")

        # Team selector
        team_selector_frame = ttk.Frame(roster_frame)
        team_selector_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(team_selector_frame, text="Select Team:").pack(side=tk.LEFT, padx=5)
        self.team_combobox = ttk.Combobox(team_selector_frame, values=self.teams_names, width=20)
        self.team_combobox.pack(side=tk.LEFT, padx=5)
        self.team_combobox.bind("<<ComboboxSelected>>", self.display_team_roster)

        # Sorting controls
        sort_frame = ttk.Frame(roster_frame)
        sort_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_combobox = ttk.Combobox(sort_frame, values=[
            "Position", "Name", "Overall", "Shooting", "Passing", "Defense", "Stamina"
        ], width=15)
        self.sort_combobox.set("Position")
        self.sort_combobox.pack(side=tk.LEFT, padx=5)
        self.sort_combobox.bind("<<ComboboxSelected>>", self.sort_roster_display)

        # Position filter
        ttk.Label(sort_frame, text="Filter:").pack(side=tk.LEFT, padx=(15, 5))
        self.roster_filter_combobox = ttk.Combobox(sort_frame, values=[
            "All Positions", "Attack", "Midfield", "Defense", "Goalie"
        ], width=12)
        self.roster_filter_combobox.set("All Positions")
        self.roster_filter_combobox.pack(side=tk.LEFT, padx=5)
        self.roster_filter_combobox.bind("<<ComboboxSelected>>", self.filter_roster_display)

        # Roster display with Overall column
        roster_columns = ("Name", "Position", "Overall", "Shooting", "Passing", "Defense", "Stamina")
        self.roster_tree = ttk.Treeview(roster_frame, columns=roster_columns, show="headings", height=20)

        # Configure column headings and make them clickable for sorting
        column_widths = {
            "Name": 150,
            "Position": 80,
            "Overall": 70,
            "Shooting": 70,
            "Passing": 70,
            "Defense": 70,
            "Stamina": 70
        }

        for col in roster_columns:
            self.roster_tree.heading(col, text=col, command=lambda c=col: self.sort_roster_by_column(c))
            if col == "Name":
                self.roster_tree.column(col, width=column_widths[col], anchor=tk.W)
            else:
                self.roster_tree.column(col, width=column_widths[col], anchor=tk.CENTER)

        # Scrollbar
        scrollbar_roster = ttk.Scrollbar(roster_frame, orient=tk.VERTICAL, command=self.roster_tree.yview)
        self.roster_tree.configure(yscrollcommand=scrollbar_roster.set)

        self.roster_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar_roster.pack(side=tk.RIGHT, fill=tk.Y)

        # Store current sort info
        self.current_sort_column = "Position"
        self.current_sort_reverse = False

    def setup_stats_tab(self):
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Player Stats")

        # Stats filter frame
        filter_frame = ttk.Frame(stats_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Filter by Team:").pack(side=tk.LEFT, padx=5)
        self.stats_team_combobox = ttk.Combobox(filter_frame, values=["All Teams"] + self.teams_names, width=20)
        self.stats_team_combobox.set("All Teams")
        self.stats_team_combobox.pack(side=tk.LEFT, padx=5)
        self.stats_team_combobox.bind("<<ComboboxSelected>>", self.filter_player_stats)

        ttk.Label(filter_frame, text="Position:").pack(side=tk.LEFT, padx=5)
        self.position_combobox = ttk.Combobox(filter_frame, values=["All Positions", "Attack", "Midfield", "Defense", "Goalie"], width=15)
        self.position_combobox.set("All Positions")
        self.position_combobox.pack(side=tk.LEFT, padx=5)
        self.position_combobox.bind("<<ComboboxSelected>>", self.filter_player_stats)

        # Player stats display
        stats_columns = ("Player", "Team", "Position", "Games", "Goals", "Assists", "Points", "Shooting", "Passing", "Defense")
        self.stats_tree = ttk.Treeview(stats_frame, columns=stats_columns, show="headings", height=20)

        for col in stats_columns:
            self.stats_tree.heading(col, text=col)
            if col in ["Player", "Team"]:
                self.stats_tree.column(col, width=120, anchor=tk.W)
            else:
                self.stats_tree.column(col, width=70, anchor=tk.CENTER)

        scrollbar_stats = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar_stats.set)

        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar_stats.pack(side=tk.RIGHT, fill=tk.Y)

    def initialize_game(self):
        """Initialize the game using your existing logic"""
        # Initialize the player name system for your teams
        initialize_rosters_for_teams(self.teams_names)

        # Create Team objects with players using your existing logic
        self.teams = []
        for name in self.teams_names:
            self.teams.append(Team(name=name, players=self.create_players(name)))

        # Generate schedule using your existing function
        raw_schedule = generate_schedule(self.teams_names, self.divisions)

        # Convert your schedule format to the GUI format
        self.schedule = self.convert_schedule_format(raw_schedule)

        # Initialize standings
        self.initialize_standings()

        # Set season progress bar maximum
        total_weeks = len(raw_schedule) if raw_schedule else 18
        self.season_progress['maximum'] = total_weeks

        self.update_all_displays()
        self.status_var.set("Season initialized - Ready to simulate!")

    def convert_schedule_format(self, raw_schedule):
        """Convert your schedule format to GUI-friendly format"""
        converted_schedule = []

        # Your schedule is: List[List[Tuple[str, str]]]
        # Each week is a list of tuples (home_team, away_team)

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
        self.standings = {}
        for team_name in self.teams_names:
            self.standings[team_name] = {
                "wins": 0,
                "losses": 0,
                "points_for": 0,
                "points_against": 0,
                "games_played": 0,
                "division": self.get_team_division(team_name)
            }

    def get_team_division(self, team_name):
        """Get the division for a team"""
        for div_name, teams in self.divisions.items():
            if team_name in teams:
                return div_name
        return "Unknown"

    def simulate_next_week(self):
        """Simulate the next week of games"""
        if self.season_complete:
            messagebox.showinfo("Season Complete", "The season has already been completed!")
            return

        self.current_week += 1

        # Get games for current week
        week_games = [game for game in self.schedule if game.get('week') == self.current_week]

        if not week_games:
            # If no more games, season is complete
            self.season_complete = True
            messagebox.showinfo("Season Complete", "Congratulations! The season has been completed.")
            self.status_var.set("Season Complete")
            return

        # Simulate games for current week (simplified simulation)
        results_text = f"Week {self.current_week} Results:\n" + "="*50 + "\n"

        import random
        for game in week_games:
            home_team = game['home_team']
            away_team = game['away_team']

            # Simple scoring simulation
            home_score = random.randint(8, 20)
            away_score = random.randint(8, 20)

            # Slight home field advantage
            home_score += random.randint(0, 2)

            # Update game results
            game["home_score"] = home_score
            game["away_score"] = away_score
            game["completed"] = True

            # Update standings
            if home_team in self.standings and away_team in self.standings:
                self.standings[home_team]["points_for"] += home_score
                self.standings[home_team]["points_against"] += away_score
                self.standings[home_team]["games_played"] += 1

                self.standings[away_team]["points_for"] += away_score
                self.standings[away_team]["points_against"] += home_score
                self.standings[away_team]["games_played"] += 1

                if home_score > away_score:
                    self.standings[home_team]["wins"] += 1
                    self.standings[away_team]["losses"] += 1
                    winner = home_team
                else:
                    self.standings[away_team]["wins"] += 1
                    self.standings[home_team]["losses"] += 1
                    winner = away_team

                results_text += f"{away_team} @ {home_team}: {away_score}-{home_score} (Winner: {winner})\n"

        # Update displays
        self.week_label.config(text=f"Current Week: {self.current_week}")
        self.season_progress['value'] = self.current_week
        self.status_var.set(f"Week {self.current_week} simulated successfully")

        # Show results
        self.recent_games_text.delete(1.0, tk.END)
        self.recent_games_text.insert(tk.END, results_text)

        self.update_all_displays()

    def simulate_entire_season(self):
        """Simulate the entire remaining season"""
        if self.season_complete:
            messagebox.showinfo("Season Complete", "The season has already been completed!")
            return

        result = messagebox.askyesno("Confirm", "Are you sure you want to simulate the entire remaining season?")
        if result:
            # Use your existing simulate_season function or simulate week by week
            try:
                # If your simulate_season function can work with current state, use it
                # simulate_season(self.schedule, self.teams)

                # Otherwise, simulate week by week
                max_weeks = 50  # Safety limit
                week_count = 0
                while not self.season_complete and week_count < max_weeks:
                    old_week = self.current_week
                    self.simulate_next_week()
                    if self.current_week == old_week:
                        break  # No more games
                    week_count += 1

                messagebox.showinfo("Season Complete", f"Season simulation completed in {week_count} weeks!")
            except Exception as e:
                messagebox.showerror("Simulation Error", f"Error during simulation: {str(e)}")

    def reset_season(self):
        """Reset the season to the beginning"""
        result = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the season? All progress will be lost.")
        if result:
            self.current_week = 0
            self.season_complete = False

            # Reinitialize everything
            self.initialize_game()

            # Update displays
            self.week_label.config(text="Current Week: 0")
            self.season_progress['value'] = 0
            self.status_var.set("Season reset - Click 'Simulate Next Week' to begin")
            self.recent_games_text.delete(1.0, tk.END)

    def update_all_displays(self):
        """Update all display elements"""
        self.update_standings_display()
        self.update_schedule_display()
        if hasattr(self, 'team_combobox') and self.team_combobox.get():
            self.display_team_roster()
        self.update_stats_display()

    def update_standings_display(self, event=None):
        """Update the standings table"""
        # Clear existing data
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)

        # Get selected division
        selected_div = self.division_combobox.get() if hasattr(self, 'division_combobox') else "All Divisions"

        # Filter teams by division if needed
        if selected_div == "All Divisions":
            teams_to_show = self.standings.items()
        else:
            teams_to_show = [(name, stats) for name, stats in self.standings.items()
                           if stats.get('division') == selected_div]

        # Sort teams by win percentage, then by point differential
        sorted_teams = sorted(teams_to_show,
                            key=lambda x: (x[1]["wins"] / max(1, x[1]["games_played"]),
                                         x[1]["points_for"] - x[1]["points_against"]),
                            reverse=True)

        for team_name, stats in sorted_teams:
            games_played = stats["games_played"]
            win_pct = f"{(stats['wins'] / max(1, games_played) * 100):.1f}%" if games_played > 0 else "0.0%"
            point_diff = stats["points_for"] - stats["points_against"]

            self.standings_tree.insert("", tk.END, values=(
                stats.get('division', 'Unknown'),
                team_name,
                stats["wins"],
                stats["losses"],
                win_pct,
                stats["points_for"],
                stats["points_against"],
                f"+{point_diff}" if point_diff >= 0 else str(point_diff)
            ))

    def update_schedule_display(self):
        """Update the schedule display"""
        # Clear existing data
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        # Get selected week
        selected_week = self.week_combobox.get() if hasattr(self, 'week_combobox') else "All Weeks"

        # Show games
        for game in self.schedule:
            week = game.get('week', 'Unknown')
            home_team = game.get('home_team', 'Unknown')
            away_team = game.get('away_team', 'Unknown')
            home_score = game.get('home_score')
            away_score = game.get('away_score')
            completed = game.get('completed', False)

            # Filter by week if selected
            if selected_week != "All Weeks" and f"Week {week}" != selected_week:
                continue

            if completed and home_score is not None and away_score is not None:
                score = f"{away_score}-{home_score}"
                status = "Final"
            else:
                score = "vs"
                status = "Scheduled"

            self.schedule_tree.insert("", tk.END, values=(
                f"Week {week}",
                home_team,
                away_team,
                score,
                status
            ))


    def calculate_overall_rating(self, player, position):
        """Calculate position-weighted overall rating"""
        shooting = getattr(player, 'shooting', 70)
        passing = getattr(player, 'passing', 70)
        defense = getattr(player, 'defense', 70)
        stamina = getattr(player, 'stamina', 70)

        # Position-specific weightings (should add up to 1.0)
        if position == "Attack":
            # Attackers: Shooting most important, then passing, stamina, defense least
            weights = {"shooting": 0.45, "passing": 0.25, "stamina": 0.20, "defense": 0.10}
        elif position == "Midfield":
            # Midfielders: Balanced, but passing and stamina more important
            weights = {"passing": 0.30, "stamina": 0.30, "shooting": 0.25, "defense": 0.15}
        elif position == "Defense":
            # Defensemen: Defense most important, then stamina, passing, shooting least
            weights = {"defense": 0.50, "stamina": 0.25, "passing": 0.15, "shooting": 0.10}
        elif position == "Goalie":
            # Goalies: Defense critical, stamina important, others less so
            weights = {"defense": 0.60, "stamina": 0.25, "passing": 0.10, "shooting": 0.05}
        else:
            # Default balanced weighting
            weights = {"shooting": 0.25, "passing": 0.25, "defense": 0.25, "stamina": 0.25}

        overall = (
            shooting * weights["shooting"] +
            passing * weights["passing"] +
            defense * weights["defense"] +
            stamina * weights["stamina"]
        )

        # Round down to 2 digits (no decimal places)
        import math
        return math.floor(overall)

    def sort_roster_by_column(self, column):
        """Sort roster by clicking column header"""
        if self.current_sort_column == column:
            # If clicking same column, reverse order
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            # New column, start with ascending order
            self.current_sort_column = column
            self.current_sort_reverse = False

        # Update the sort combobox to match
        self.sort_combobox.set(column)

        # Re-display roster with new sort
        self.display_team_roster()

    def sort_roster_display(self, event=None):
        """Sort roster when dropdown selection changes"""
        self.current_sort_column = self.sort_combobox.get()
        self.current_sort_reverse = False  # Reset to ascending when using dropdown
        self.display_team_roster()

    def filter_roster_display(self, event=None):
        """Filter roster by position"""
        self.display_team_roster()

    def display_team_roster(self, event=None):
        """Display roster for selected team with sorting and filtering"""
        selected_team = self.team_combobox.get()
        if not selected_team:
            return

        # Clear existing data
        for item in self.roster_tree.get_children():
            self.roster_tree.delete(item)

        # Find the team object
        team_obj = None
        for team in self.teams:
            if team.name == selected_team:
                team_obj = team
                break

        if not team_obj or not hasattr(team_obj, 'players'):
            return

        # Get filter setting
        position_filter = self.roster_filter_combobox.get() if hasattr(self, 'roster_filter_combobox') else "All Positions"

        # Filter players by position if needed
        filtered_players = []
        for player in team_obj.players:
            if position_filter == "All Positions" or player.position == position_filter:
                filtered_players.append(player)

        # Calculate overall ratings and prepare data for sorting
        player_data = []
        for player in filtered_players:
            overall = self.calculate_overall_rating(player, player.position)
            player_data.append({
                'player': player,
                'name': player.name,
                'position': player.position,
                'overall': overall,
                'shooting': getattr(player, 'shooting', 'N/A'),
                'passing': getattr(player, 'passing', 'N/A'),
                'defense': getattr(player, 'defense', 'N/A'),
                'stamina': getattr(player, 'stamina', 'N/A')
            })

        # Sort the data
        sort_column = getattr(self, 'current_sort_column', 'Position')
        reverse_sort = getattr(self, 'current_sort_reverse', False)

        if sort_column == "Name":
            player_data.sort(key=lambda x: x['name'], reverse=reverse_sort)
        elif sort_column == "Position":
            # Custom position order: Attack, Midfield, Defense, Goalie
            position_order = {"Attack": 1, "Midfield": 2, "Defense": 3, "Goalie": 4}
            player_data.sort(key=lambda x: (position_order.get(x['position'], 5), x['name']), reverse=reverse_sort)
        elif sort_column == "Overall":
            player_data.sort(key=lambda x: x['overall'], reverse=reverse_sort)
        elif sort_column in ["Shooting", "Passing", "Defense", "Stamina"]:
            attr_name = sort_column.lower()
            player_data.sort(key=lambda x: getattr(x['player'], attr_name, 0), reverse=reverse_sort)

        # Display sorted and filtered players
        for data in player_data:
            self.roster_tree.insert("", tk.END, values=(
                data['name'],
                data['position'],
                data['overall'],
                data['shooting'],
                data['passing'],
                data['defense'],
                data['stamina']
            ))

        # Update team summary
        self.update_roster_summary(filtered_players, selected_team)

    def update_roster_summary(self, players, team_name):
        """Update roster summary information"""
        if not players:
            return

        # Count by position
        position_counts = {"Attack": 0, "Midfield": 0, "Defense": 0, "Goalie": 0}
        total_overall = 0

        for player in players:
            position_counts[player.position] += 1
            total_overall += self.calculate_overall_rating(player, player.position)

        # Round down average overall to whole number
        import math
        avg_overall = math.floor(total_overall / len(players)) if players else 0

        # You can display this info in the status bar or add a summary label
        summary = f"{team_name}: {len(players)} players | Avg Overall: {avg_overall} | "
        summary += f"A:{position_counts['Attack']} M:{position_counts['Midfield']} D:{position_counts['Defense']} G:{position_counts['Goalie']}"

        # Update status bar with summary
        if hasattr(self, 'status_var'):
            current_status = self.status_var.get()
            if "simulated" in current_status.lower() or "ready" in current_status.lower():
                self.status_var.set(summary)

    def update_stats_display(self):
        """Update the player stats display"""
        # Clear existing data
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        # Get filter values
        selected_team = self.stats_team_combobox.get() if hasattr(self, 'stats_team_combobox') else "All Teams"
        selected_position = self.position_combobox.get() if hasattr(self, 'position_combobox') else "All Positions"

        # Display player stats from all teams
        for team in self.teams:
            if selected_team != "All Teams" and team.name != selected_team:
                continue

            for player in team.players:
                if selected_position != "All Positions" and player.position != selected_position:
                    continue

                # For now, show base stats (you can extend this with game stats later)
                self.stats_tree.insert("", tk.END, values=(
                    player.name,
                    team.name,
                    player.position,
                    0,  # Games (to be implemented)
                    0,  # Goals (to be implemented)
                    0,  # Assists (to be implemented)
                    0,  # Points (to be implemented)
                    getattr(player, 'shooting', 'N/A'),
                    getattr(player, 'passing', 'N/A'),
                    getattr(player, 'defense', 'N/A')
                ))

    def display_week_schedule(self, event=None):
        """Display schedule for selected week"""
        self.update_schedule_display()

    def filter_player_stats(self, event=None):
        """Filter player stats by team and position"""
        self.update_stats_display()

    def new_season(self):
        """Start a new season"""
        self.reset_season()
        messagebox.showinfo("New Season", "New season started!")

    def save_game(self):
        """Save the current game state"""
        save_data = {
            "current_week": self.current_week,
            "season_complete": self.season_complete,
            "standings": self.standings,
            "schedule": self.schedule  # Note: This might need serialization depending on your schedule format
        }

        try:
            with open("lacrosse_save.json", "w") as f:
                json.dump(save_data, f, indent=2, default=str)
            messagebox.showinfo("Save Game", "Game saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving game: {str(e)}")

    def load_game(self):
        """Load a saved game state"""
        try:
            if os.path.exists("lacrosse_save.json"):
                with open("lacrosse_save.json", "r") as f:
                    save_data = json.load(f)

                self.current_week = save_data["current_week"]
                self.season_complete = save_data["season_complete"]
                self.standings = save_data["standings"]
                # Note: You might need to regenerate schedule or handle serialization

                # Update displays
                self.week_label.config(text=f"Current Week: {self.current_week}")
                self.season_progress['value'] = self.current_week
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
