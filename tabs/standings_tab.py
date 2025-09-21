import tkinter as tk
from tkinter import ttk

class StandingsTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        standings_frame = ttk.Frame(notebook)
        notebook.add(standings_frame, text="Standings")

        # Division selector
        div_frame = ttk.Frame(standings_frame)
        div_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(div_frame, text="View Division:").pack(side=tk.LEFT, padx=5)
        self.division_combobox = ttk.Combobox(div_frame, values=["All Divisions"] + list(self.main_gui.divisions.keys()), width=20)
        self.division_combobox.set("All Divisions")
        self.division_combobox.pack(side=tk.LEFT, padx=5)
        self.division_combobox.bind("<<ComboboxSelected>>", self.update_display)

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

    def update_display(self, event=None):
        """Update the standings table"""
        # Clear existing data
        for item in self.standings_tree.get_children():
            self.standings_tree.delete(item)

        # Get selected division
        selected_div = self.division_combobox.get()

        # Filter teams by division if needed
        if selected_div == "All Divisions":
            teams_to_show = self.main_gui.standings.items()
        else:
            teams_to_show = [(name, stats) for name, stats in self.main_gui.standings.items()
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
