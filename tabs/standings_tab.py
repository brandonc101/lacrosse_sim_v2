import tkinter as tk
from tkinter import ttk

class StandingsTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        standings_frame = ttk.Frame(notebook)
        notebook.add(standings_frame, text="Standings")

        # Filter frame
        filter_frame = ttk.Frame(standings_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Conference filter
        ttk.Label(filter_frame, text="Conference:").pack(side=tk.LEFT, padx=5)
        self.conference_combobox = ttk.Combobox(filter_frame, values=["All Conferences", "Eastern", "Western"], width=15)
        self.conference_combobox.set("All Conferences")
        self.conference_combobox.pack(side=tk.LEFT, padx=5)
        self.conference_combobox.bind("<<ComboboxSelected>>", self.on_conference_change)

        # Division filter
        ttk.Label(filter_frame, text="Division:").pack(side=tk.LEFT, padx=5)
        self.division_combobox = ttk.Combobox(filter_frame, values=["All Divisions"], width=15)
        self.division_combobox.set("All Divisions")
        self.division_combobox.pack(side=tk.LEFT, padx=5)
        self.division_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Sort options
        ttk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT, padx=(20, 5))
        self.sort_combobox = ttk.Combobox(filter_frame, values=["Points", "Wins", "Win %", "Goals For", "Goal Diff"], width=12)
        self.sort_combobox.set("Points")
        self.sort_combobox.pack(side=tk.LEFT, padx=5)
        self.sort_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Standings display
        columns = ("Team", "Conference", "Division", "GP", "W", "L", "OTL", "PTS", "GF", "GA", "DIFF", "Win %")
        self.standings_tree = ttk.Treeview(standings_frame, columns=columns, show="headings", height=15)

        # Configure columns
        column_widths = {
            "Team": 150, "Conference": 90, "Division": 80, "GP": 40, "W": 40, "L": 40,
            "OTL": 40, "PTS": 50, "GF": 50, "GA": 50, "DIFF": 60, "Win %": 70
        }

        for col in columns:
            self.standings_tree.heading(col, text=col)
            if col == "Team":
                self.standings_tree.column(col, width=column_widths[col], anchor=tk.W)
            else:
                self.standings_tree.column(col, width=column_widths[col], anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(standings_frame, orient=tk.VERTICAL, command=self.standings_tree.yview)
        self.standings_tree.configure(yscrollcommand=scrollbar.set)

        self.standings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def on_conference_change(self, event=None):
        """Update division options when conference changes"""
        selected_conference = self.conference_combobox.get()

        if selected_conference == "All Conferences":
            division_values = ["All Divisions"]
        elif selected_conference in self.main_gui.conferences:
            divisions = list(self.main_gui.conferences[selected_conference].keys())
            division_values = ["All Divisions"] + divisions
        else:
            division_values = ["All Divisions"]

        self.division_combobox['values'] = division_values
        self.division_combobox.set("All Divisions")
        self.update_display()

    def update_display(self, event=None):
        """Update the standings display with filtering and sorting"""
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)

        selected_conference = self.conference_combobox.get()
        selected_division = self.division_combobox.get()
        sort_by = self.sort_combobox.get()

        # Collect team data
        team_data = []
        for team in self.main_gui.teams:
            team_conference = self.main_gui.get_team_conference(team.name)
            team_division = self.main_gui.get_team_division(team.name)

            # Apply filters
            if selected_conference != "All Conferences" and team_conference != selected_conference:
                continue
            if selected_division != "All Divisions" and team_division != selected_division:
                continue

            # Calculate stats
            games_played = team.wins + team.losses + getattr(team, 'overtime_losses', 0)
            win_percentage = (team.wins / games_played * 100) if games_played > 0 else 0
            goal_diff = team.goals_for - team.goals_against
            points = team.wins * 2 + getattr(team, 'overtime_losses', 0)

            team_data.append({
                'name': team.name,
                'conference': team_conference,
                'division': team_division,
                'games_played': games_played,
                'wins': team.wins,
                'losses': team.losses,
                'overtime_losses': getattr(team, 'overtime_losses', 0),
                'points': points,
                'goals_for': team.goals_for,
                'goals_against': team.goals_against,
                'goal_diff': goal_diff,
                'win_pct': win_percentage
            })

        # Sort the data
        if sort_by == "Points":
            team_data.sort(key=lambda x: (x['points'], x['win_pct'], x['goal_diff']), reverse=True)
        elif sort_by == "Wins":
            team_data.sort(key=lambda x: (x['wins'], x['win_pct'], x['goal_diff']), reverse=True)
        elif sort_by == "Win %":
            team_data.sort(key=lambda x: (x['win_pct'], x['points'], x['goal_diff']), reverse=True)
        elif sort_by == "Goals For":
            team_data.sort(key=lambda x: x['goals_for'], reverse=True)
        elif sort_by == "Goal Diff":
            team_data.sort(key=lambda x: x['goal_diff'], reverse=True)

        # Display the data
        for data in team_data:
            self.standings_tree.insert("", tk.END, values=(
                data['name'],
                data['conference'],
                data['division'],
                data['games_played'],
                data['wins'],
                data['losses'],
                data['overtime_losses'],
                data['points'],
                data['goals_for'],
                data['goals_against'],
                f"{data['goal_diff']:+d}",
                f"{data['win_pct']:.1f}%"
            ))
