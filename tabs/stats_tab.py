import tkinter as tk
from tkinter import ttk

class StatsTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Player Stats")

        # Stats filter frame
        filter_frame = ttk.Frame(stats_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # First row of filters
        filter_row1 = ttk.Frame(filter_frame)
        filter_row1.pack(fill=tk.X, pady=2)

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

        # Team filter
        ttk.Label(filter_row1, text="Team:").pack(side=tk.LEFT, padx=5)
        self.stats_team_combobox = ttk.Combobox(filter_row1, values=["All Teams"], width=20)
        self.stats_team_combobox.set("All Teams")
        self.stats_team_combobox.pack(side=tk.LEFT, padx=5)
        self.stats_team_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Position filter
        ttk.Label(filter_row1, text="Position:").pack(side=tk.LEFT, padx=5)
        self.position_combobox = ttk.Combobox(filter_row1, values=["All Positions", "Attack", "Midfield", "Defense", "Goalie"], width=15)
        self.position_combobox.set("All Positions")
        self.position_combobox.pack(side=tk.LEFT, padx=5)
        self.position_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Second row of filters - Sort by stats
        filter_row2 = ttk.Frame(filter_frame)
        filter_row2.pack(fill=tk.X, pady=2)

        ttk.Label(filter_row2, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_stat_combobox = ttk.Combobox(filter_row2, values=[
            "Player Name", "Goals", "Assists", "Points", "Saves", "Save %", "GAA", "Games"
        ], width=15)
        self.sort_stat_combobox.set("Points")
        self.sort_stat_combobox.pack(side=tk.LEFT, padx=5)
        self.sort_stat_combobox.bind("<<ComboboxSelected>>", self.update_display)

        ttk.Label(filter_row2, text="Order:").pack(side=tk.LEFT, padx=5)
        self.sort_order_combobox = ttk.Combobox(filter_row2, values=["Highest First", "Lowest First"], width=12)
        self.sort_order_combobox.set("Highest First")
        self.sort_order_combobox.pack(side=tk.LEFT, padx=5)
        self.sort_order_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Minimum threshold filter
        ttk.Label(filter_row2, text="Min Value:").pack(side=tk.LEFT, padx=(15, 5))
        self.min_value_var = tk.StringVar(value="0")
        self.min_value_entry = ttk.Entry(filter_row2, textvariable=self.min_value_var, width=8)
        self.min_value_entry.pack(side=tk.LEFT, padx=5)
        self.min_value_entry.bind("<KeyRelease>", self.update_display)

        # Player stats display - Added Save % and GAA columns
        stats_columns = ("Player", "Team", "Position", "Games", "Goals", "Assists", "Points", "Saves", "Save %", "GAA")
        self.stats_tree = ttk.Treeview(stats_frame, columns=stats_columns, show="headings", height=20)

        # Configure columns - make them clickable for sorting
        column_widths = {
            "Player": 140,
            "Team": 110,
            "Position": 80,
            "Games": 60,
            "Goals": 60,
            "Assists": 60,
            "Points": 60,
            "Saves": 60,
            "Save %": 70,
            "GAA": 70
        }

        for col in stats_columns:
            self.stats_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            if col in ["Player", "Team"]:
                self.stats_tree.column(col, width=column_widths[col], anchor=tk.W)
            else:
                self.stats_tree.column(col, width=column_widths[col], anchor=tk.CENTER)

        scrollbar_stats = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar_stats.set)

        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar_stats.pack(side=tk.RIGHT, fill=tk.Y)

    def sort_by_column(self, column):
        """Sort stats by clicking column header"""
        self.sort_stat_combobox.set(column)
        # Toggle sort order if clicking same column
        current_order = self.sort_order_combobox.get()
        if hasattr(self, '_last_sort_column') and self._last_sort_column == column:
            new_order = "Lowest First" if current_order == "Highest First" else "Highest First"
            self.sort_order_combobox.set(new_order)
        self._last_sort_column = column
        self.update_display()

    def on_conference_change(self, event=None):
        """Update division and team options when conference changes"""
        selected_conference = self.conference_combobox.get()

        # Update division options
        if selected_conference == "All Conferences":
            division_values = ["All Divisions"]
            team_values = ["All Teams"] + self.main_gui.teams_names
        elif selected_conference in self.main_gui.conferences:
            divisions = list(self.main_gui.conferences[selected_conference].keys())
            division_values = ["All Divisions"] + divisions
            # Get teams from this conference
            conference_teams = self.main_gui.get_conference_teams(selected_conference)
            team_values = ["All Teams"] + conference_teams
        else:
            division_values = ["All Divisions"]
            team_values = ["All Teams"]

        self.division_combobox['values'] = division_values
        self.division_combobox.set("All Divisions")
        self.stats_team_combobox['values'] = team_values
        self.stats_team_combobox.set("All Teams")
        self.update_display()

    def on_division_change(self, event=None):
        """Update team options when division changes"""
        selected_conference = self.conference_combobox.get()
        selected_division = self.division_combobox.get()

        if selected_division == "All Divisions":
            if selected_conference == "All Conferences":
                team_values = ["All Teams"] + self.main_gui.teams_names
            else:
                conference_teams = self.main_gui.get_conference_teams(selected_conference)
                team_values = ["All Teams"] + conference_teams
        else:
            if selected_conference != "All Conferences" and selected_conference in self.main_gui.conferences:
                division_teams = self.main_gui.get_division_teams(selected_conference, selected_division)
                team_values = ["All Teams"] + division_teams
            else:
                team_values = ["All Teams"]

        self.stats_team_combobox['values'] = team_values
        self.stats_team_combobox.set("All Teams")
        self.update_display()

    def calculate_save_percentage(self, player):
        """Calculate save percentage for goalies"""
        if player.position != "Goalie":
            return None

        saves = getattr(player, 'saves', 0)
        goals_against = getattr(player, 'goals_against', 0)
        shots_faced = saves + goals_against

        if shots_faced == 0:
            return 0.0

        return (saves / shots_faced) * 100

    def calculate_gaa(self, player):
        """Calculate Goals Against Average for goalies"""
        if player.position != "Goalie":
            return None

        goals_against = getattr(player, 'goals_against', 0)
        minutes_played = getattr(player, 'minutes_played', 0)

        if minutes_played == 0:
            return 0.0

        # GAA = (Goals Against × Game Length) / Minutes Played
        # Assuming standard game is 60 minutes
        return (goals_against * 60) / minutes_played

    def update_display(self, event=None):
        """Update the player stats display with filtering and sorting"""
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        selected_conference = self.conference_combobox.get()
        selected_division = self.division_combobox.get()
        selected_team = self.stats_team_combobox.get()
        selected_position = self.position_combobox.get()
        sort_by = self.sort_stat_combobox.get()
        sort_order = self.sort_order_combobox.get()

        # Get minimum value filter
        try:
            min_value = float(self.min_value_var.get()) if self.min_value_var.get() else 0
        except ValueError:
            min_value = 0

        # Collect all player data
        player_data = []
        for team in self.main_gui.teams:
            team_conference = self.main_gui.get_team_conference(team.name)
            team_division = self.main_gui.get_team_division(team.name)

            # Apply conference filter
            if selected_conference != "All Conferences" and team_conference != selected_conference:
                continue

            # Apply division filter
            if selected_division != "All Divisions" and team_division != selected_division:
                continue

            # Apply team filter
            if selected_team != "All Teams" and team.name != selected_team:
                continue

            for player in team.players:
                if selected_position != "All Positions" and player.position != selected_position:
                    continue

                # Get player stats
                games_played = getattr(player, 'games_played', 0)
                goals = getattr(player, 'goals', 0)
                assists = getattr(player, 'assists', 0)
                points = goals + assists
                saves = getattr(player, 'saves', 0) if player.position == "Goalie" else 0

                # Calculate goalie-specific stats
                save_percentage = self.calculate_save_percentage(player)
                gaa = self.calculate_gaa(player)

                # Apply minimum value filter based on sort column
                filter_value = 0
                if sort_by == "Goals":
                    filter_value = goals
                elif sort_by == "Assists":
                    filter_value = assists
                elif sort_by == "Points":
                    filter_value = points
                elif sort_by == "Saves":
                    filter_value = saves if player.position == "Goalie" else 0
                elif sort_by == "Save %":
                    filter_value = save_percentage if save_percentage is not None else 0
                elif sort_by == "GAA":
                    filter_value = gaa if gaa is not None else 0
                elif sort_by == "Games":
                    filter_value = games_played

                # Skip if below minimum threshold
                if filter_value < min_value:
                    continue

                # Format display values
                save_pct_display = f"{save_percentage:.1f}%" if save_percentage is not None else "-"
                gaa_display = f"{gaa:.2f}" if gaa is not None else "-"

                player_data.append({
                    'name': player.name,
                    'team': team.name,
                    'position': player.position,
                    'games': games_played,
                    'goals': goals,
                    'assists': assists,
                    'points': points,
                    'saves': saves if player.position == "Goalie" else "-",
                    'save_pct': save_percentage if save_percentage is not None else 0,
                    'save_pct_display': save_pct_display,
                    'gaa': gaa if gaa is not None else 0,
                    'gaa_display': gaa_display
                })

        # Sort the data
        reverse_sort = sort_order == "Highest First"

        if sort_by == "Player Name":
            player_data.sort(key=lambda x: x['name'], reverse=reverse_sort)
        elif sort_by == "Goals":
            player_data.sort(key=lambda x: x['goals'], reverse=reverse_sort)
        elif sort_by == "Assists":
            player_data.sort(key=lambda x: x['assists'], reverse=reverse_sort)
        elif sort_by == "Points":
            player_data.sort(key=lambda x: x['points'], reverse=reverse_sort)
        elif sort_by == "Saves":
            # For saves, only sort goalies and put non-goalies at the end
            goalies = [p for p in player_data if p['position'] == "Goalie"]
            non_goalies = [p for p in player_data if p['position'] != "Goalie"]
            goalies.sort(key=lambda x: x['saves'] if isinstance(x['saves'], int) else 0, reverse=reverse_sort)
            player_data = goalies + non_goalies
        elif sort_by == "Save %":
            # For save %, only sort goalies and put non-goalies at the end
            goalies = [p for p in player_data if p['position'] == "Goalie"]
            non_goalies = [p for p in player_data if p['position'] != "Goalie"]
            goalies.sort(key=lambda x: x['save_pct'], reverse=reverse_sort)
            player_data = goalies + non_goalies
        elif sort_by == "GAA":
            # For GAA, sort lowest first by default (lower GAA is better), put non-goalies at end
            goalies = [p for p in player_data if p['position'] == "Goalie"]
            non_goalies = [p for p in player_data if p['position'] != "Goalie"]
            # For GAA, flip the reverse logic since lower is better
            gaa_reverse = not reverse_sort if sort_order == "Highest First" else reverse_sort
            goalies.sort(key=lambda x: x['gaa'], reverse=gaa_reverse)
            player_data = goalies + non_goalies
        elif sort_by == "Games":
            player_data.sort(key=lambda x: x['games'], reverse=reverse_sort)

        # Display sorted and filtered data
        for data in player_data:
            self.stats_tree.insert("", tk.END, values=(
                data['name'],
                data['team'],
                data['position'],
                data['games'],
                data['goals'],
                data['assists'],
                data['points'],
                data['saves'],
                data['save_pct_display'],
                data['gaa_display']
            ))
