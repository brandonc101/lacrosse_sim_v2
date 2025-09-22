# ===== 1. tabs/playoff_bracket_tab.py =====
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
        title_label = ttk.Label(self.bracket_frame, text="🏆 PLAYOFF BRACKET 🏆",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Bracket display
        bracket_container = ttk.Frame(self.bracket_frame)
        bracket_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.bracket_text = tk.Text(bracket_container, height=25, width=100,
                                   font=("Courier", 9), wrap=tk.NONE)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(bracket_container, orient="vertical",
                                   command=self.bracket_text.yview)
        h_scrollbar = ttk.Scrollbar(bracket_container, orient="horizontal",
                                   command=self.bracket_text.xview)

        self.bracket_text.configure(yscrollcommand=v_scrollbar.set,
                                   xscrollcommand=h_scrollbar.set)

        # Pack scrollbars and text
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.bracket_text.pack(fill=tk.BOTH, expand=True)

        # Update button
        update_btn = ttk.Button(self.bracket_frame, text="Refresh Bracket",
                               command=self.update_display)
        update_btn.pack(pady=5)

        # Initial bracket display
        self.update_display()

    def update_display(self):
        """Update the playoff bracket display"""
        playoff_teams = self._get_playoff_teams()
        bracket_content = self._generate_bracket_display(playoff_teams)

        self.bracket_text.delete(1.0, tk.END)
        self.bracket_text.insert(tk.END, bracket_content)

    def _get_playoff_teams(self):
        """Get playoff teams based on current standings"""
        playoff_teams = {
            "Eastern": {"North": "TBD", "South": "TBD"},
            "Western": {"North": "TBD", "South": "TBD"}
        }

        if not hasattr(self.main_gui, 'standings') or not self.main_gui.standings:
            return playoff_teams

        try:
            # Group teams by division
            divisions = {
                "Eastern North": [],
                "Eastern South": [],
                "Western North": [],
                "Western South": []
            }

            for team_name, team_data in self.main_gui.standings.items():
                div = team_data.get('division', 'Unknown')
                if div in divisions:
                    divisions[div].append({
                        'name': team_name,
                        'wins': team_data.get('wins', 0),
                        'losses': team_data.get('losses', 0),
                        'points': team_data.get('wins', 0) * 2 + team_data.get('overtime_losses', 0)
                    })

            # Get division winners (top team in each division)
            for div_name, teams in divisions.items():
                if teams:
                    teams.sort(key=lambda x: x['points'], reverse=True)
                    winner = teams[0]

                    if div_name == "Eastern North":
                        playoff_teams["Eastern"]["North"] = winner
                    elif div_name == "Eastern South":
                        playoff_teams["Eastern"]["South"] = winner
                    elif div_name == "Western North":
                        playoff_teams["Western"]["North"] = winner
                    elif div_name == "Western South":
                        playoff_teams["Western"]["South"] = winner

        except Exception as e:
            print(f"Error getting playoff teams: {e}")

        return playoff_teams

    def _generate_bracket_display(self, playoff_teams):
        """Generate the ASCII bracket display"""
        # Get team names with padding
        en_team = playoff_teams["Eastern"]["North"]
        en_name = en_team['name'] if isinstance(en_team, dict) else str(en_team)
        en_record = f"({en_team['wins']}-{en_team['losses']})" if isinstance(en_team, dict) else ""

        es_team = playoff_teams["Eastern"]["South"]
        es_name = es_team['name'] if isinstance(es_team, dict) else str(es_team)
        es_record = f"({es_team['wins']}-{es_team['losses']})" if isinstance(es_team, dict) else ""

        wn_team = playoff_teams["Western"]["North"]
        wn_name = wn_team['name'] if isinstance(wn_team, dict) else str(wn_team)
        wn_record = f"({wn_team['wins']}-{wn_team['losses']})" if isinstance(wn_team, dict) else ""

        ws_team = playoff_teams["Western"]["South"]
        ws_name = ws_team['name'] if isinstance(ws_team, dict) else str(ws_team)
        ws_record = f"({ws_team['wins']}-{ws_team['losses']})" if isinstance(ws_team, dict) else ""

        bracket = f"""
╔════════════════════════════════════════════════════════════════════════════════════════╗
║                                 🏆 LACROSSE PLAYOFFS 🏆                                ║
║                              Single Elimination Tournament                              ║
╚════════════════════════════════════════════════════════════════════════════════════════╝

PLAYOFF FORMAT:
• Week 14: Conference Semifinals (Division Winners)
• Week 15: Conference Finals
• Week 16: Championship Game

═══════════════════════════════════════════════════════════════════════════════════════════

CONFERENCE SEMIFINALS (Week 14)

Eastern Conference:                              Western Conference:

┌────────────────────────────┐                  ┌────────────────────────────┐
│ {en_name:<20} │                  │ {wn_name:<20} │
│ {en_record:<20} │                  │ {wn_record:<20} │
└────────────────────────────┘                  └────────────────────────────┘
              │                                                │
              │                                                │
              ▼                                                ▼
┌────────────────────────────┐                  ┌────────────────────────────┐
│ {es_name:<20} │                  │ {ws_name:<20} │
│ {es_record:<20} │                  │ {ws_record:<20} │
└────────────────────────────┘                  └────────────────────────────┘
              │                                                │
              │                                                │
              └────────────────┐              ┌─────────────────┘
                               │              │
                               ▼              ▼

CONFERENCE FINALS (Week 15)

              ┌────────────────────────────┐
              │     Eastern Champion       │
              │          TBD               │
              └────────────────────────────┘
                              │
                              │
                              ▼
              ┌────────────────────────────┐
              │     Western Champion       │
              │          TBD               │
              └────────────────────────────┘
                              │
                              │
                              ▼

CHAMPIONSHIP GAME (Week 16)

              ┌────────────────────────────┐
              │       CHAMPION             │
              │         TBD                │
              │                            │
              │    🏆 TROPHY 🏆           │
              └────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════

Current Week: {self.main_gui.current_week}
"""

        # Add current playoff results if available
        if hasattr(self.main_gui, 'playoff_schedule') and self.main_gui.playoff_schedule:
            bracket += "\nPLAYOFF RESULTS:\n"
            bracket += "═" * 50 + "\n"

            for game in self.main_gui.playoff_schedule:
                if game.get('completed', False):
                    home = game['home_team']
                    away = game['away_team']
                    home_score = game.get('home_score', 0)
                    away_score = game.get('away_score', 0)
                    week = game.get('week', 0)
                    round_name = game.get('round', 'Game')

                    winner = home if home_score > away_score else away
                    bracket += f"Week {week} - {round_name}: {away} @ {home} ({away_score}-{home_score}) - Winner: {winner}\n"

        return bracket
