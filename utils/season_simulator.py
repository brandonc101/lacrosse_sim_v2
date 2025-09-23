from models.match import simulate_match

class SeasonSimulator:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def simulate_next_week(self):
        """Simulate the next week of games including playoffs"""
        if self.main_gui.season_complete:
            return None

        self.main_gui.current_week += 1

        if self.main_gui.current_week <= 14:
            return self._simulate_regular_season_week()
        elif self.main_gui.current_week == 15:
            return self._simulate_playoff_prep_week()
        elif self.main_gui.current_week <= 18:
            return self._simulate_playoff_week()
        else:
            return self._simulate_offseason_week()

    def simulate_entire_season(self):
        """Simulate the entire remaining season"""
        max_weeks = 50
        week_count = 0

        while not self.main_gui.season_complete and week_count < max_weeks:
            old_week = self.main_gui.current_week
            result = self.simulate_next_week()
            week_count += 1

            if self.main_gui.current_week == old_week:
                break

        return week_count

    def _simulate_regular_season_week(self):
        """Simulate a regular season week"""
        week_games = [game for game in self.main_gui.schedule if game.get('week') == self.main_gui.current_week]

        if not week_games:
            if self.main_gui.current_week == 14:
                return self._end_regular_season()
            else:
                return f"Week {self.main_gui.current_week}: Some teams have bye weeks this week."

        return self._simulate_games(week_games, "Regular Season")

    def _simulate_playoff_prep_week(self):
        """Handle the transition week between regular season and playoffs"""
        # Generate playoff schedule and show tabs
        self.main_gui.playoff_schedule = self.main_gui.game_simulator.playoff_system.generate_playoff_schedule()

        # Initialize playoff stats for all players
        self._initialize_playoff_stats()

        # Show playoff tabs
        self._show_playoff_tabs()

        return f"Week 15: Playoff Preparation Week\n" + \
               "Regular season complete! Playoff seeding finalized.\n" + \
               "Top 4 teams from each conference qualified.\n" + \
               "Conference Semifinals begin next week!\n\n" + \
               self.main_gui.game_simulator.playoff_system.get_playoff_bracket_text()

    def _initialize_playoff_stats(self):
        """Initialize separate playoff stats for all players"""
        for team in self.main_gui.teams:
            for player in team.players:
                # Initialize playoff-specific stats if they don't exist
                if not hasattr(player, 'playoff_goals'):
                    player.playoff_goals = 0
                    player.playoff_assists = 0
                    player.playoff_saves = 0
                    player.playoff_games_played = 0
                    player.playoff_goals_against = 0 if player.position == "Goalie" else None
                    player.playoff_minutes_played = 0 if player.position == "Goalie" else None

    def _simulate_playoff_week(self):
        """Simulate a playoff week"""
        # Generate next round matchups if needed
        if hasattr(self.main_gui.game_simulator, 'playoff_system'):
            self.main_gui.game_simulator.playoff_system.advance_playoffs()

        # Get games for this week
        week_games = [game for game in self.main_gui.playoff_schedule if game.get('week') == self.main_gui.current_week]

        if not week_games:
            if self.main_gui.current_week == 18:
                self.main_gui.season_complete = True
                return "Championship complete! Season finished."
            return f"Week {self.main_gui.current_week}: No playoff games scheduled."

        return self._simulate_games(week_games, "Playoffs")

    def _simulate_offseason_week(self):
        """Handle offseason weeks"""
        if self.main_gui.current_week == 19:
            return "Week 19: Offseason begins. Draft preparation in progress..."
        elif self.main_gui.current_week == 20:
            return "Week 20: Draft week. New players entering the league..."
        else:
            self.main_gui.season_complete = True
            return "Season cycle complete."

    def _end_regular_season(self):
        """Handle end of regular season"""
        return f"Regular season complete! Playoff preparation begins next week."

    def _show_playoff_tabs(self):
        """Show playoff tabs when playoffs begin"""
        if hasattr(self.main_gui, 'tab_manager'):
            self.main_gui.tab_manager.show_playoff_tabs()

    def _simulate_games(self, week_games, phase_name):
        """Simulate a list of games"""
        results_text = f"Week {self.main_gui.current_week} {phase_name} Results:\n" + "="*50 + "\n"

        for game in week_games:
            home_team_name = game['home_team']
            away_team_name = game['away_team']

            if "TBD" in home_team_name or "TBD" in away_team_name:
                results_text += f"{game.get('round', 'Game')}: Waiting for previous round to complete\n"
                continue

            home_team, away_team = self._find_teams(home_team_name, away_team_name)

            if home_team and away_team:
                results_text += self._simulate_single_game(game, home_team, away_team, phase_name)

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

    def _simulate_single_game(self, game, home_team, away_team, phase_name):
        """Simulate a single game with proper stat tracking"""
        # Determine if this is a playoff game
        is_playoff = self.main_gui.current_week > 15

        # Pass is_playoff flag to simulate_match
        match_result = simulate_match(home_team, away_team, is_playoff=is_playoff)

        game["home_score"] = match_result.home_score
        game["away_score"] = match_result.away_score
        game["completed"] = True

        # Update standings only for regular season games
        if self.main_gui.current_week <= 14:
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
        if self.main_gui.current_week > 15:
            status_text += f" - {phase_name}"
        self.main_gui.status_var.set(status_text)

    def _get_current_playoff_matchups(self):
        """Get current playoff matchups as text"""
        if not hasattr(self.main_gui, 'playoff_schedule'):
            return "No playoff matchups available"

        matchup_text = "CURRENT PLAYOFF MATCHUPS:\n"
        matchup_text += "-" * 30 + "\n"

        for game in self.main_gui.playoff_schedule:
            if not game.get('completed', False):
                round_name = game.get('round', 'Game')
                home = game.get('home_team', 'TBD')
                away = game.get('away_team', 'TBD')
                week = game.get('week', 0)
                matchup_text += f"Week {week} - {round_name}: {away} @ {home}\n"

        return matchup_text
