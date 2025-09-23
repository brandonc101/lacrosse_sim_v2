import tkinter as tk
from tkinter import ttk

class PlayoffBracketTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        self.bracket_frame = ttk.Frame(notebook)
        notebook.add(self.bracket_frame, text="Playoff Bracket")

        # Title
        title_label = ttk.Label(self.bracket_frame, text="PLAYOFF BRACKET & SEEDING",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Bracket display
        self.bracket_text = tk.Text(self.bracket_frame, height=25, width=90,
                                   font=("Courier", 10))
        self.bracket_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Update button
        update_btn = ttk.Button(self.bracket_frame, text="Refresh Bracket",
                               command=self.update_display)
        update_btn.pack(pady=5)

        # Initial display
        self.update_display()

    def update_display(self):
        """Update the playoff bracket display"""
        self.bracket_text.delete(1.0, tk.END)

        if not hasattr(self.main_gui, 'playoff_schedule') or not self.main_gui.playoff_schedule:
            self.bracket_text.insert(tk.END, "Playoffs begin after the regular season (Week 15)")
            return

        # Get playoff system info
        if hasattr(self.main_gui, 'game_simulator') and hasattr(self.main_gui.game_simulator, 'playoff_system'):
            bracket_info = self.main_gui.game_simulator.playoff_system.get_playoff_bracket_text()
            self.bracket_text.insert(tk.END, bracket_info)

            # Add current results
            self.bracket_text.insert(tk.END, "\n\nCURRENT RESULTS:\n")
            self.bracket_text.insert(tk.END, "=" * 40 + "\n")

            # Group games by week
            weeks = {}
            for game in self.main_gui.playoff_schedule:
                week = game.get('week', 0)
                if week not in weeks:
                    weeks[week] = []
                weeks[week].append(game)

            # Show results by week
            for week in sorted(weeks.keys()):
                week_name = {16: "Conference Semifinals", 17: "Conference Finals", 18: "Championship"}
                self.bracket_text.insert(tk.END, f"\n{week_name.get(week, f'Week {week}')} (Week {week}):\n")

                for game in weeks[week]:
                    home = game.get('home_team', 'TBD')
                    away = game.get('away_team', 'TBD')

                    if game.get('completed', False):
                        home_score = game.get('home_score', 0)
                        away_score = game.get('away_score', 0)
                        winner = home if home_score > away_score else away
                        self.bracket_text.insert(tk.END, f"  {away} @ {home}: {away_score}-{home_score} (Winner: {winner})\n")
                    else:
                        if "TBD" not in home and "TBD" not in away:
                            self.bracket_text.insert(tk.END, f"  {away} @ {home}: Not yet played\n")
                        else:
                            self.bracket_text.insert(tk.END, f"  Waiting for previous round to complete\n")
        else:
            self.bracket_text.insert(tk.END, "Playoff system not available")
