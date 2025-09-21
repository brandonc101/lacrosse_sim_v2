import tkinter as tk
from tkinter import ttk
import math
from utils.calculations import calculate_overall_rating

class RosterTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)
        self.current_sort_column = "Position"
        self.current_sort_reverse = False

    def setup_tab(self, notebook):
        roster_frame = ttk.Frame(notebook)
        notebook.add(roster_frame, text="Team Roster")

        # Team selector
        team_selector_frame = ttk.Frame(roster_frame)
        team_selector_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(team_selector_frame, text="Select Team:").pack(side=tk.LEFT, padx=5)
        self.team_combobox = ttk.Combobox(team_selector_frame, values=self.main_gui.teams_names, width=20)
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

        # Roster display
        roster_columns = ("Name", "Position", "Overall", "Shooting", "Passing", "Defense", "Stamina")
        self.roster_tree = ttk.Treeview(roster_frame, columns=roster_columns, show="headings", height=20)

        column_widths = {
            "Name": 150, "Position": 80, "Overall": 70,
            "Shooting": 70, "Passing": 70, "Defense": 70, "Stamina": 70
        }

        for col in roster_columns:
            self.roster_tree.heading(col, text=col, command=lambda c=col: self.sort_roster_by_column(c))
            if col == "Name":
                self.roster_tree.column(col, width=column_widths[col], anchor=tk.W)
            else:
                self.roster_tree.column(col, width=column_widths[col], anchor=tk.CENTER)

        scrollbar_roster = ttk.Scrollbar(roster_frame, orient=tk.VERTICAL, command=self.roster_tree.yview)
        self.roster_tree.configure(yscrollcommand=scrollbar_roster.set)

        self.roster_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar_roster.pack(side=tk.RIGHT, fill=tk.Y)

    def sort_roster_by_column(self, column):
        if self.current_sort_column == column:
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            self.current_sort_column = column
            self.current_sort_reverse = False
        self.sort_combobox.set(column)
        self.display_team_roster()

    def sort_roster_display(self, event=None):
        self.current_sort_column = self.sort_combobox.get()
        self.current_sort_reverse = False
        self.display_team_roster()

    def filter_roster_display(self, event=None):
        self.display_team_roster()

    def display_team_roster(self, event=None):
        selected_team = self.team_combobox.get()
        if not selected_team:
            return

        for item in self.roster_tree.get_children():
            self.roster_tree.delete(item)

        team_obj = None
        for team in self.main_gui.teams:
            if team.name == selected_team:
                team_obj = team
                break

        if not team_obj or not hasattr(team_obj, 'players'):
            return

        position_filter = self.roster_filter_combobox.get()
        filtered_players = [p for p in team_obj.players
                          if position_filter == "All Positions" or p.position == position_filter]

        player_data = []
        for player in filtered_players:
            overall = calculate_overall_rating(player, player.position)
            player_data.append({
                'player': player, 'name': player.name, 'position': player.position,
                'overall': overall, 'shooting': getattr(player, 'shooting', 'N/A'),
                'passing': getattr(player, 'passing', 'N/A'),
                'defense': getattr(player, 'defense', 'N/A'),
                'stamina': getattr(player, 'stamina', 'N/A')
            })

        self._sort_player_data(player_data)

        for data in player_data:
            self.roster_tree.insert("", tk.END, values=(
                data['name'], data['position'], data['overall'],
                data['shooting'], data['passing'], data['defense'], data['stamina']
            ))

        self._update_roster_summary(filtered_players, selected_team)

    def _sort_player_data(self, player_data):
        sort_column = self.current_sort_column
        reverse_sort = self.current_sort_reverse

        if sort_column == "Name":
            player_data.sort(key=lambda x: x['name'], reverse=reverse_sort)
        elif sort_column == "Position":
            position_order = {"Attack": 1, "Midfield": 2, "Defense": 3, "Goalie": 4}
            player_data.sort(key=lambda x: (position_order.get(x['position'], 5), x['name']), reverse=reverse_sort)
        elif sort_column == "Overall":
            player_data.sort(key=lambda x: x['overall'], reverse=reverse_sort)
        elif sort_column in ["Shooting", "Passing", "Defense", "Stamina"]:
            attr_name = sort_column.lower()
            player_data.sort(key=lambda x: getattr(x['player'], attr_name, 0), reverse=reverse_sort)

    def _update_roster_summary(self, players, team_name):
        if not players:
            return

        position_counts = {"Attack": 0, "Midfield": 0, "Defense": 0, "Goalie": 0}
        total_overall = sum(calculate_overall_rating(p, p.position) for p in players)
        for player in players:
            position_counts[player.position] += 1

        avg_overall = math.floor(total_overall / len(players)) if players else 0
        summary = f"{team_name}: {len(players)} players | Avg Overall: {avg_overall} | "
        summary += f"A:{position_counts['Attack']} M:{position_counts['Midfield']} D:{position_counts['Defense']} G:{position_counts['Goalie']}"
        self.main_gui.status_var.set(summary)

    def update_display(self):
        if hasattr(self, 'team_combobox') and self.team_combobox.get():
            self.display_team_roster()
