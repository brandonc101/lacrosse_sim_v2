import tkinter as tk
from tkinter import ttk

class ScheduleTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="Schedule")

        # Filter frame
        filter_frame = ttk.Frame(schedule_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # First row of filters
        filter_row1 = ttk.Frame(filter_frame)
        filter_row1.pack(fill=tk.X, pady=2)

        # View type filter
        ttk.Label(filter_row1, text="View:").pack(side=tk.LEFT, padx=5)
        self.view_type_combobox = ttk.Combobox(filter_row1, values=["All Games", "Team Schedule"], width=15)
        self.view_type_combobox.set("All Games")
        self.view_type_combobox.pack(side=tk.LEFT, padx=5)
        self.view_type_combobox.bind("<<ComboboxSelected>>", self.on_view_type_change)

        # Conference filter
        ttk.Label(filter_row1, text="Conference:").pack(side=tk.LEFT, padx=5)
        self.conference_combobox = ttk.Combobox(filter_row1, values=["All Conferences", "Eastern", "Western"], width=15)
        self.conference_combobox.set("All Conferences")
        self.conference_combobox.pack(side=tk.LEFT, padx=5)
        self.conference_combobox.bind("<<ComboboxSelected>>", self.on_conference_change)

        # Division filter
        ttk.Label(filter_row1, text="Division:").pack(side=tk.LEFT, padx=5)
        self.division_combobox = ttk.Combobox(filter_row1, values=["All Divisions"], width=15)
        self.division_combobox.set("All Divisions")
        self.division_combobox.pack(side=tk.LEFT, padx=5)
        self.division_combobox.bind("<<ComboboxSelected>>", self.on_division_change)

        # Team filter (for team-specific view)
        ttk.Label(filter_row1, text="Team:").pack(side=tk.LEFT, padx=5)
        self.team_combobox = ttk.Combobox(filter_row1, values=["Select Team"], width=20)
        self.team_combobox.set("Select Team")
        self.team_combobox.pack(side=tk.LEFT, padx=5)
        self.team_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Second row of filters
        filter_row2 = ttk.Frame(filter_frame)
        filter_row2.pack(fill=tk.X, pady=2)

        # Week filter (updated for 16 weeks)
        ttk.Label(filter_row2, text="Week:").pack(side=tk.LEFT, padx=5)
        self.week_combobox = ttk.Combobox(filter_row2, values=["All Weeks"] + [f"Week {i}" for i in range(1, 16)], width=12)
        # CHANGED from range(1, 20) to range(1, 16)
        self.week_combobox.set("All Weeks")
        self.week_combobox.pack(side=tk.LEFT, padx=5)
        self.week_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Status filter
        ttk.Label(filter_row2, text="Status:").pack(side=tk.LEFT, padx=5)
        self.status_combobox = ttk.Combobox(filter_row2, values=["All Games", "Completed", "Upcoming"], width=12)
        self.status_combobox.set("All Games")
        self.status_combobox.pack(side=tk.LEFT, padx=5)
        self.status_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Schedule display
        columns = ("Week", "Date", "Home Team", "Away Team", "Home Score", "Away Score", "Status")
        self.schedule_tree = ttk.Treeview(schedule_frame, columns=columns, show="headings", height=18)

        # Configure columns
        column_widths = {
            "Week": 60, "Date": 100, "Home Team": 150, "Away Team": 150,
            "Home Score": 80, "Away Score": 80, "Status": 100
        }

        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=column_widths[col], anchor=tk.CENTER)

        # Left-align team names for better readability
        self.schedule_tree.column("Home Team", anchor=tk.W)
        self.schedule_tree.column("Away Team", anchor=tk.W)

        # Scrollbar
        scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)

        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initially disable team filter
        self.team_combobox.configure(state="disabled")

    def on_view_type_change(self, event=None):
        """Handle view type change between All Games and Team Schedule"""
        view_type = self.view_type_combobox.get()

        if view_type == "Team Schedule":
            # Enable team filter and update team options
            self.team_combobox.configure(state="readonly")
            self.update_team_options()
        else:
            # Disable team filter
            self.team_combobox.configure(state="disabled")
            self.team_combobox.set("Select Team")

        self.update_display()

    def on_conference_change(self, event=None):
        """Update division and team options when conference changes"""
        selected_conference = self.conference_combobox.get()

        # Update division options
        if selected_conference == "All Conferences":
            division_values = ["All Divisions"]
        elif hasattr(self.main_gui, 'conferences') and selected_conference in self.main_gui.conferences:
            divisions = list(self.main_gui.conferences[selected_conference].keys())
            division_values = ["All Divisions"] + divisions
        else:
            division_values = ["All Divisions"]

        self.division_combobox['values'] = division_values
        self.division_combobox.set("All Divisions")

        # Update team options if in team view
        if self.view_type_combobox.get() == "Team Schedule":
            self.update_team_options()

        self.update_display()

    def on_division_change(self, event=None):
        """Update team options when division changes"""
        # Update team options if in team view
        if self.view_type_combobox.get() == "Team Schedule":
            self.update_team_options()

        self.update_display()

    def update_team_options(self):
        """Update team dropdown based on conference/division filters"""
        selected_conference = self.conference_combobox.get()
        selected_division = self.division_combobox.get()

        if selected_division != "All Divisions" and selected_conference != "All Conferences":
            # Show teams from specific division
            if (hasattr(self.main_gui, 'conferences') and
                selected_conference in self.main_gui.conferences and
                selected_division in self.main_gui.conferences[selected_conference]):
                team_values = self.main_gui.conferences[selected_conference][selected_division]
            else:
                team_values = []
        elif selected_conference != "All Conferences":
            # Show teams from entire conference
            team_values = self.main_gui.get_conference_teams(selected_conference)
        else:
            # Show all teams
            team_values = getattr(self.main_gui, 'teams_names', [])

        self.team_combobox['values'] = team_values
        if team_values and self.team_combobox.get() not in team_values:
            self.team_combobox.set(team_values[0] if team_values else "Select Team")

    def get_opponent_and_location(self, game, team_name):
        """Get opponent and home/away status for a specific team"""
        if game.get('home_team') == team_name:
            return game.get('away_team'), "vs", "Home"
        else:
            return game.get('home_team'), "@", "Away"

    def update_display(self, event=None):
        """Update the schedule display with filtering"""
        # Clear existing items
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        # Check if schedule exists
        if not hasattr(self.main_gui, 'schedule') or not self.main_gui.schedule:
            self.schedule_tree.insert("", tk.END, values=(
                "No schedule", "available", "yet", "", "", "", ""
            ))
            return

        view_type = self.view_type_combobox.get()
        selected_conference = self.conference_combobox.get()
        selected_division = self.division_combobox.get()
        selected_team = self.team_combobox.get()
        selected_week = self.week_combobox.get()
        selected_status = self.status_combobox.get()

        # Filter games
        filtered_games = []
        for game in self.main_gui.schedule:
            # Apply week filter
            if selected_week != "All Weeks":
                week_num = int(selected_week.split()[1])
                if game.get('week', 0) != week_num:
                    continue

            # Apply status filter
            if selected_status != "All Games":
                is_completed = game.get('completed', False)
                if selected_status == "Completed" and not is_completed:
                    continue
                elif selected_status == "Upcoming" and is_completed:
                    continue

            # Apply view type specific filters
            if view_type == "Team Schedule":
                # Show only games for selected team
                if selected_team == "Select Team" or selected_team not in [game.get('home_team', ''), game.get('away_team', '')]:
                    continue
            else:
                # Apply conference/division filters for all games view
                home_team = game.get('home_team', '')
                away_team = game.get('away_team', '')

                # Check if either team matches conference filter
                if selected_conference != "All Conferences":
                    home_conf = self.main_gui.get_team_conference(home_team)
                    away_conf = self.main_gui.get_team_conference(away_team)
                    if selected_conference not in [home_conf, away_conf]:
                        continue

                # Check if either team matches division filter
                if selected_division != "All Divisions":
                    home_div = self.main_gui.get_team_division(home_team)
                    away_div = self.main_gui.get_team_division(away_team)
                    if selected_division not in [home_div, away_div]:
                        continue

            filtered_games.append(game)

        # Sort games by week and date
        filtered_games.sort(key=lambda x: (x.get('week', 0), x.get('date', '')))

        # Display games
        for game in filtered_games:
            week = game.get('week', 'TBD')
            date = game.get('date', 'TBD')
            home_team = game.get('home_team', 'TBD')
            away_team = game.get('away_team', 'TBD')
            home_score = game.get('home_score', '')
            away_score = game.get('away_score', '')
            completed = game.get('completed', False)

            # Format date nicely
            if date != 'TBD':
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%b %d")
                except:
                    formatted_date = date
            else:
                formatted_date = date

            # Format scores
            if completed and home_score is not None and away_score is not None:
                home_score_str = str(home_score)
                away_score_str = str(away_score)
                status = "Final"
            else:
                home_score_str = "-"
                away_score_str = "-"
                status = "Scheduled"

            # Special formatting for team schedule view
            if view_type == "Team Schedule" and selected_team != "Select Team":
                opponent, vs_at, location = self.get_opponent_and_location(game, selected_team)
                # Show vs/@ to indicate home/away
                if location == "Home":
                    display_home = selected_team
                    display_away = f"vs {away_team}"
                else:
                    display_home = f"@ {home_team}"
                    display_away = selected_team
            else:
                display_home = home_team
                display_away = away_team

            self.schedule_tree.insert("", tk.END, values=(
                f"Week {week}",
                formatted_date,
                display_home,
                display_away,
                home_score_str,
                away_score_str,
                status
            ))
