from models.match import simulate_match

class SeasonSimulator:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def simulate_next_week(self):
        """Simulate the next week of games including playoffs"""
        if self.main_gui.season_complete:
            return None

        self.main_gui.current_week += 1

        if self.main_gui.current_week <= 12:
            return self._simulate_regular_season_week()
        elif self.main_gui.current_week <= 15:
            return self._simulate_playoff_week()
        else:
            return self._simulate_offseason_week()

    def simulate_entire_season(self):
        """Simulate the entire remaining season"""
        max_weeks = 50
        week_count = 0

        while not self.main_gui.season_complete and week_count < max_weeks:
            old_week = self.main_gui.current_week
            self.simulate_next_week()
            if self.main_gui.current_week == old_week:
                break
            week_count += 1

        return week_count

    def _simulate_regular_season_week(self):
        """Simulate a regular season week"""
        week_games = [game for game in self.main_gui.schedule if game.get('week') == self.main_gui.current_week]

        if not week_games:
            if self.main_gui.current_week == 12:
                return self._end_regular_season()
            else:
                return f"Week {self.main_gui.current_week}: Some teams have bye weeks this week."

        return self._simulate_games(week_games, "Regular Season")

    def _simulate_playoff_week(self):
        """Simulate a playoff week"""
        if not hasattr(self.main_gui, 'playoff_schedule') or not self.main_gui.playoff_schedule:
            self.main_gui.playoff_schedule = self.main_gui.game_simulator.playoff_system.generate_playoff_schedule()

        week_games = [game for game in self.main_gui.playoff_schedule if game.get('week') == self.main_gui.current_week]

        if not week_games:
            if self.main_gui.current_week == 15:
                self.main_gui.season_complete = True
                return "Championship complete! Season finished."
            return f"No playoff games scheduled for week {self.main_gui.current_week}"

        return self._simulate_games(week_games, "Playoffs")

    def _simulate_offseason_week(self):
        """Handle offseason weeks"""
        if self.main_gui.current_week == 16:
            return "Week 16: Offseason begins. Draft preparation in progress..."
        elif self.main_gui.current_week == 17:
            return "Week 17: Draft week. New players entering the league..."
        else:
            self.main_gui.season_complete = True
            return "Season cycle complete."

    def _end_regular_season(self):
        """Handle end of regular season"""
        self.main_gui.playoff_schedule = self.main_gui.game_simulator.playoff_system.generate_playoff_schedule()
        return f"Regular season complete! Playoff bracket generated.\n{self._get_playoff_bracket_text()}"

    def _simulate_games(self, week_games, phase_name):
        """Simulate a list of games"""
        results_text = f"Week {self.main_gui.current_week} {phase_name} Results:\n" + "="*50 + "\n"

        for game in week_games:
            home_team_name = game['home_team']
            away_team_name = game['away_team']

            if "TBD" in home_team_name or "TBD" in away_team_name:
                results_text += f"{game.get('round', 'Game')}: {away_team_name} @ {home_team_name}\n"
                continue

            home_team, away_team = self._find_teams(home_team_name, away_team_name)

            if home_team and away_team:
                results_text += self._simulate_single_game(game, home_team, away_team)

        self._update_status(phase_name)
        return results_text

    def _find_teams(self, home_name, away_name):
        """Find team objects by name"""
        home_team = away_team = None
        for team in self.main_gui.teams:
            if team.name == home_name:
                home_team = team
            elif team.name == away_name:
                away_team = team
        return home_team, away_team

    def _simulate_single_game(self, game, home_team, away_team):
        """Simulate a single game"""
        match_result = simulate_match(home_team, away_team)

        game["home_score"] = match_result.home_score
        game["away_score"] = match_result.away_score
        game["completed"] = True

        if self.main_gui.current_week <= 12:
            self._update_standings_from_match(home_team, away_team, match_result)

        overtime_text = " (OT)" if match_result.overtime else ""
        winner = home_team.name if match_result.home_score > match_result.away_score else away_team.name

        result_text = ""
        round_text = game.get('round', '')
        if round_text:
            result_text += f"{round_text}: "

        result_text += f"{away_team.name} @ {home_team.name}: {match_result.away_score}-{match_result.home_score}{overtime_text} (Winner: {winner})\n"
        result_text += f"  Shots: {home_team.name} {match_result.home_shots}, {away_team.name} {match_result.away_shots}\n"

        return result_text

    def _update_standings_from_match(self, home_team, away_team, match_result):
        """Update standings after a match"""
        for team_name, team in [(home_team.name, home_team), (away_team.name, away_team)]:
            if team_name in self.main_gui.standings:
                self.main_gui.standings[team_name].update({
                    "wins": team.wins,
                    "losses": team.losses + team.overtime_losses,
                    "points_for": team.goals_for,
                    "points_against": team.goals_against,
                    "games_played": team.wins + team.losses + team.overtime_losses,
                    "overtime_losses": team.overtime_losses
                })

    def _update_status(self, phase_name):
        """Update GUI status"""
        status_text = f"Week {self.main_gui.current_week} {phase_name.lower()} simulated successfully"
        if self.main_gui.current_week > 12:
            status_text += f" - {phase_name}"
        self.main_gui.status_var.set(status_text)

    def _get_playoff_bracket_text(self):
        """Generate playoff bracket text"""
        return "Playoff bracket generated..."
