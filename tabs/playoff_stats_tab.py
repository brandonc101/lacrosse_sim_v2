import tkinter as tk
from tkinter import ttk

class PlayoffStatsTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        self.stats_frame = ttk.Frame(notebook)
        notebook.add(self.stats_frame, text="Playoff Stats")

        # Title
        title_label = ttk.Label(self.stats_frame, text="PLAYOFF STATISTICS",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Create notebook for different stat categories
        self.stats_notebook = ttk.Notebook(self.stats_frame)
        self.stats_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Player Stats Tab
        self._setup_player_stats_tab()

        # Team Stats Tab
        self._setup_team_stats_tab()

        # Game Results Tab
        self._setup_game_results_tab()

    def _setup_player_stats_tab(self):
        """Setup player playoff statistics tab"""
        player_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(player_frame, text="Player Stats")

        # Player stats treeview
        columns = ('Player', 'Team', 'Position', 'Games', 'Goals', 'Assists', 'Points', 'Saves')
        self.player_tree = ttk.Treeview(player_frame, columns=columns, show='headings', height=15)

        # Configure columns
        col_widths = {'Player': 150, 'Team': 120, 'Position': 80, 'Games': 60,
                     'Goals': 60, 'Assists': 60, 'Points': 60, 'Saves': 60}

        for col in columns:
            self.player_tree.heading(col, text=col)
            self.player_tree.column(col, width=col_widths.get(col, 80), anchor='center')

        # Scrollbar for player stats
        player_scrollbar = ttk.Scrollbar(player_frame, orient="vertical", command=self.player_tree.yview)
        self.player_tree.configure(yscrollcommand=player_scrollbar.set)

        # Pack player stats
        self.player_tree.pack(side="left", fill=tk.BOTH, expand=True)
        player_scrollbar.pack(side="right", fill="y")

    def _setup_team_stats_tab(self):
        """Setup team playoff statistics tab"""
        team_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(team_frame, text="Team Stats")

        # Team stats treeview
        columns = ('Team', 'Games', 'Wins', 'Losses', 'Goals For', 'Goals Against', 'Goal Diff')
        self.team_tree = ttk.Treeview(team_frame, columns=columns, show='headings', height=10)

        # Configure columns
        for col in columns:
            self.team_tree.heading(col, text=col)
            self.team_tree.column(col, width=100, anchor='center')

        # Scrollbar for team stats
        team_scrollbar = ttk.Scrollbar(team_frame, orient="vertical", command=self.team_tree.yview)
        self.team_tree.configure(yscrollcommand=team_scrollbar.set)

        # Pack team stats
        self.team_tree.pack(side="left", fill=tk.BOTH, expand=True)
        team_scrollbar.pack(side="right", fill="y")

    def _setup_game_results_tab(self):
        """Setup playoff game results tab"""
        results_frame = ttk.Frame(self.stats_notebook)
        self.stats_notebook.add(results_frame, text="Game Results")

        # Results text area
        self.results_text = tk.Text(results_frame, height=20, width=80, font=("Courier", 10))

        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)

        # Pack results
        self.results_text.pack(side="left", fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side="right", fill="y")

    def update_display(self):
        """Update all playoff statistics"""
        self._update_player_stats()
        self._update_team_stats()
        self._update_game_results()

    def _update_player_stats(self):
        """Update player playoff statistics using SEPARATE playoff stats"""
        # Clear existing data
        for item in self.player_tree.get_children():
            self.player_tree.delete(item)

        if not hasattr(self.main_gui, 'teams') or not self.main_gui.teams:
            return

        # Get playoff teams and their players with playoff stats
        playoff_players = []
        for team in self.main_gui.teams:
            for player in team.players:
                if hasattr(player, 'playoff_games_played') and player.playoff_games_played > 0:
                    playoff_goals = getattr(player, 'playoff_goals', 0)
                    playoff_assists = getattr(player, 'playoff_assists', 0)
                    playoff_points = playoff_goals + playoff_assists
                    playoff_saves = getattr(player, 'playoff_saves', 0)

                    playoff_players.append((
                        player.name, team.name, player.position,
                        player.playoff_games_played, playoff_goals,
                        playoff_assists, playoff_points, playoff_saves
                    ))

        # Sort by points (goals + assists) for playoffs only
        playoff_players.sort(key=lambda x: x[6], reverse=True)

        # Insert into treeview
        for player_info in playoff_players:
            self.player_tree.insert('', 'end', values=player_info)

    def _update_team_stats(self):
        """Update team playoff statistics"""
        # Clear existing data
        for item in self.team_tree.get_children():
            self.team_tree.delete(item)

        if not hasattr(self.main_gui, 'playoff_schedule') or not self.main_gui.playoff_schedule:
            return

        # Calculate team stats from playoff games only
        team_stats = {}

        for game in self.main_gui.playoff_schedule:
            if game.get('completed', False):
                home_team = game['home_team']
                away_team = game['away_team']
                home_score = game.get('home_score', 0)
                away_score = game.get('away_score', 0)

                # Initialize team stats if needed
                for team in [home_team, away_team]:
                    if team not in team_stats:
                        team_stats[team] = {
                            'games': 0, 'wins': 0, 'losses': 0,
                            'goals_for': 0, 'goals_against': 0
                        }

                # Update stats
                team_stats[home_team]['games'] += 1
                team_stats[away_team]['games'] += 1
                team_stats[home_team]['goals_for'] += home_score
                team_stats[home_team]['goals_against'] += away_score
                team_stats[away_team]['goals_for'] += away_score
                team_stats[away_team]['goals_against'] += home_score

                # Update wins/losses
                if home_score > away_score:
                    team_stats[home_team]['wins'] += 1
                    team_stats[away_team]['losses'] += 1
                else:
                    team_stats[away_team]['wins'] += 1
                    team_stats[home_team]['losses'] += 1

        # Insert team stats into treeview
        for team, stats in sorted(team_stats.items()):
            goal_diff = stats['goals_for'] - stats['goals_against']
            goal_diff_str = f"+{goal_diff}" if goal_diff > 0 else str(goal_diff)

            self.team_tree.insert('', 'end', values=(
                team, stats['games'], stats['wins'], stats['losses'],
                stats['goals_for'], stats['goals_against'], goal_diff_str
            ))

    def _update_game_results(self):
        """Update playoff game results"""
        self.results_text.delete(1.0, tk.END)

        if not hasattr(self.main_gui, 'playoff_schedule') or not self.main_gui.playoff_schedule:
            self.results_text.insert(tk.END, "No playoff games scheduled yet.")
            return

        results_content = "PLAYOFF GAME RESULTS\n"
        results_content += "=" * 50 + "\n\n"

        # Group games by week/round
        games_by_week = {}
        for game in self.main_gui.playoff_schedule:
            week = game.get('week', 0)
            if week not in games_by_week:
                games_by_week[week] = []
            games_by_week[week].append(game)

        # Display results by week
        for week in sorted(games_by_week.keys()):
            if week == 16:
                results_content += "CONFERENCE SEMIFINALS (Week 16)\n"
            elif week == 17:
                results_content += "\nCONFERENCE FINALS (Week 17)\n"
            elif week == 18:
                results_content += "\nCHAMPIONSHIP GAME (Week 18)\n"

            results_content += "-" * 30 + "\n"

            for game in games_by_week[week]:
                home_team = game['home_team']
                away_team = game['away_team']

                if game.get('completed', False):
                    home_score = game.get('home_score', 0)
                    away_score = game.get('away_score', 0)
                    winner = home_team if home_score > away_score else away_team
                    results_content += f"{away_team} @ {home_team}: {away_score}-{home_score} (Winner: {winner})\n"
                else:
                    results_content += f"{away_team} @ {home_team}: Not yet played\n"

            results_content += "\n"

        self.results_text.insert(tk.END, results_content)
