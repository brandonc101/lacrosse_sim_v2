import tkinter as tk
from tkinter import ttk

class ScheduleTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        schedule_frame = ttk.Frame(notebook)
        notebook.add(schedule_frame, text="Schedule")

        # Week selector
        week_selector_frame = ttk.Frame(schedule_frame)
        week_selector_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(week_selector_frame, text="Select Week:").pack(side=tk.LEFT, padx=5)
        self.week_combobox = ttk.Combobox(week_selector_frame, values=["All Weeks"] + [f"Week {i}" for i in range(1, 19)], width=15)
        self.week_combobox.set("All Weeks")
        self.week_combobox.pack(side=tk.LEFT, padx=5)
        self.week_combobox.bind("<<ComboboxSelected>>", self.update_display)

        # Schedule display with Date column
        schedule_columns = ("Week", "Date", "Home Team", "Away Team", "Score", "Status")
        self.schedule_tree = ttk.Treeview(schedule_frame, columns=schedule_columns, show="headings", height=20)

        for col in schedule_columns:
            self.schedule_tree.heading(col, text=col)
            if col in ["Home Team", "Away Team"]:
                self.schedule_tree.column(col, width=150, anchor=tk.W)
            elif col == "Score":
                self.schedule_tree.column(col, width=120, anchor=tk.CENTER)
            elif col == "Date":
                self.schedule_tree.column(col, width=100, anchor=tk.CENTER)
            else:
                self.schedule_tree.column(col, width=80, anchor=tk.CENTER)

        scrollbar_schedule = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar_schedule.set)

        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar_schedule.pack(side=tk.RIGHT, fill=tk.Y)

    def update_display(self, event=None):
        """Update the schedule display including playoffs"""
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)

        selected_week = self.week_combobox.get()

        # Show regular season games
        for game in self.main_gui.schedule:
            week = game.get('week', 'Unknown')
            if week > 13:  # Skip weeks beyond regular season
                continue

            date = game.get('date', 'TBD')
            home_team = game.get('home_team', 'Unknown')
            away_team = game.get('away_team', 'Unknown')
            home_score = game.get('home_score')
            away_score = game.get('away_score')
            completed = game.get('completed', False)

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
                date,
                home_team,
                away_team,
                score,
                status
            ))

        # Show playoff games
        if hasattr(self.main_gui, 'playoff_schedule') and self.main_gui.playoff_schedule:
            for game in self.main_gui.playoff_schedule:
                week = game.get('week', 'Unknown')
                round_name = game.get('round', 'Playoff Game')
                home_team = game.get('home_team', 'TBD')
                away_team = game.get('away_team', 'TBD')
                home_score = game.get('home_score')
                away_score = game.get('away_score')
                completed = game.get('completed', False)

                if selected_week != "All Weeks" and f"Week {week}" != selected_week:
                    continue

                if completed and home_score is not None and away_score is not None:
                    score = f"{away_score}-{home_score}"
                    status = "Final"
                else:
                    score = "vs"
                    status = "Scheduled"

                # Use round name as "date" for playoffs
                self.schedule_tree.insert("", tk.END, values=(
                    f"Week {week}",
                    round_name,
                    home_team,
                    away_team,
                    score,
                    status
                ))
