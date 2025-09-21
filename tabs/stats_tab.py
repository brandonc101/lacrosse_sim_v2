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

        ttk.Label(filter_frame, text="Filter by Team:").pack(side=tk.LEFT, padx=5)
        self.stats_team_combobox = ttk.Combobox(filter_frame, values=["All Teams"] + self.main_gui.teams_names, width=20)
        self.stats_team_combobox.set("All Teams")
        self.stats_team_combobox.pack(side=tk.LEFT, padx=5)
        self.stats_team_combobox.bind("<<ComboboxSelected>>", self.update_display)

        ttk.Label(filter_frame, text="Position:").pack(side=tk.LEFT, padx=5)
        self.position_combobox = ttk.Combobox(filter_frame, values=["All Positions", "Attack", "Midfield", "Defense", "Goalie"], width=15)
        self.position_combobox.set("All Positions")
        self.position_combobox.pack(side=tk.LEFT, padx=5)
        self.position_combobox.bind("<<ComboboxSelected>>", self.update_display)

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

    def update_display(self, event=None):
        """Update the player stats display"""
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        selected_team = self.stats_team_combobox.get()
        selected_position = self.position_combobox.get()

        for team in self.main_gui.teams:
            if selected_team != "All Teams" and team.name != selected_team:
                continue

            for player in team.players:
                if selected_position != "All Positions" and player.position != selected_position:
                    continue

                # Show actual stats from match simulation
                games_played = getattr(player, 'games_played', 0)
                goals = getattr(player, 'goals', 0)
                assists = getattr(player, 'assists', 0)
                points = goals + assists
                saves = getattr(player, 'saves', 0) if player.position == "Goalie" else "-"

                self.stats_tree.insert("", tk.END, values=(
                    player.name,
                    team.name,
                    player.position,
                    games_played,
                    goals,
                    assists,
                    points,
                    getattr(player, 'shooting', 'N/A'),
                    getattr(player, 'passing', 'N/A'),
                    getattr(player, 'defense', 'N/A')
                ))
