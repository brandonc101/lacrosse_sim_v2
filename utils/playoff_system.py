from datetime import datetime, timedelta

class PlayoffSystem:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def generate_playoff_schedule(self):
        """Generate playoff schedule with 4 teams per conference"""
        playoff_teams = self._get_playoff_teams()
        playoff_schedule = []

        # Week 16: Conference Semifinals (1v4, 2v3 in each conference)

        # Eastern Conference Semifinals
        if len(playoff_teams["Eastern"]) >= 4:
            east_1v4 = {
                "week": 16,
                "date": self._get_playoff_date(16),
                "round": "Eastern Conference Semifinal",
                "home_team": playoff_teams["Eastern"][0]['name'],  # 1 seed (home)
                "away_team": playoff_teams["Eastern"][3]['name'],  # 4 seed (away)
                "home_score": None,
                "away_score": None,
                "completed": False,
                "series_id": "E1v4"
            }

            east_2v3 = {
                "week": 16,
                "date": self._get_playoff_date(16),
                "round": "Eastern Conference Semifinal",
                "home_team": playoff_teams["Eastern"][1]['name'],  # 2 seed (home)
                "away_team": playoff_teams["Eastern"][2]['name'],  # 3 seed (away)
                "home_score": None,
                "away_score": None,
                "completed": False,
                "series_id": "E2v3"
            }

            playoff_schedule.extend([east_1v4, east_2v3])

        # Western Conference Semifinals
        if len(playoff_teams["Western"]) >= 4:
            west_1v4 = {
                "week": 16,
                "date": self._get_playoff_date(16),
                "round": "Western Conference Semifinal",
                "home_team": playoff_teams["Western"][0]['name'],  # 1 seed (home)
                "away_team": playoff_teams["Western"][3]['name'],  # 4 seed (away)
                "home_score": None,
                "away_score": None,
                "completed": False,
                "series_id": "W1v4"
            }

            west_2v3 = {
                "week": 16,
                "date": self._get_playoff_date(16),
                "round": "Western Conference Semifinal",
                "home_team": playoff_teams["Western"][1]['name'],  # 2 seed (home)
                "away_team": playoff_teams["Western"][2]['name'],  # 3 seed (away)
                "home_score": None,
                "away_score": None,
                "completed": False,
                "series_id": "W2v3"
            }

            playoff_schedule.extend([west_1v4, west_2v3])

        return playoff_schedule

    def advance_playoffs(self):
        """Generate next round based on completed games"""
        if not hasattr(self.main_gui, 'playoff_schedule'):
            return

        current_week = self.main_gui.current_week

        # Generate Week 17 Conference Finals
        if current_week == 17:
            week_16_complete = self._check_week_complete(16)
            if week_16_complete and not self._week_games_exist(17):
                eastern_winner = self._get_conference_semifinal_winners("Eastern")
                western_winner = self._get_conference_semifinal_winners("Western")

                if len(eastern_winner) == 2:  # Both Eastern semifinals complete
                    east_final = {
                        "week": 17,
                        "date": self._get_playoff_date(17),
                        "round": "Eastern Conference Final",
                        "home_team": self._get_higher_seed(eastern_winner),
                        "away_team": self._get_lower_seed(eastern_winner),
                        "home_score": None,
                        "away_score": None,
                        "completed": False
                    }
                    self.main_gui.playoff_schedule.append(east_final)

                if len(western_winner) == 2:  # Both Western semifinals complete
                    west_final = {
                        "week": 17,
                        "date": self._get_playoff_date(17),
                        "round": "Western Conference Final",
                        "home_team": self._get_higher_seed(western_winner),
                        "away_team": self._get_lower_seed(western_winner),
                        "home_score": None,
                        "away_score": None,
                        "completed": False
                    }
                    self.main_gui.playoff_schedule.append(west_final)

        # Generate Week 18 Championship
        elif current_week == 18:
            week_17_complete = self._check_week_complete(17)
            if week_17_complete and not self._week_games_exist(18):
                conference_winners = self._get_conference_final_winners()

                if len(conference_winners) == 2:  # Both conference finals complete
                    championship = {
                        "week": 18,
                        "date": self._get_playoff_date(18),
                        "round": "Championship Game",
                        "home_team": conference_winners[0],  # First winner gets home field
                        "away_team": conference_winners[1],
                        "home_score": None,
                        "away_score": None,
                        "completed": False
                    }
                    self.main_gui.playoff_schedule.append(championship)

    def _get_playoff_teams(self):
        """Get top 4 teams from each conference (2 division winners + 2 wild cards)"""
        playoff_teams = {
            "Eastern": [],
            "Western": []
        }

        if not hasattr(self.main_gui, 'standings') or not self.main_gui.standings:
            return playoff_teams

        try:
            # Get all teams with their conference
            eastern_teams = []
            western_teams = []

            for team_name, team_data in self.main_gui.standings.items():
                team_info = {
                    'name': team_name,
                    'wins': team_data.get('wins', 0),
                    'losses': team_data.get('losses', 0),
                    'overtime_losses': team_data.get('overtime_losses', 0),
                    'points': team_data.get('wins', 0) * 2 + team_data.get('overtime_losses', 0),
                    'goals_for': team_data.get('points_for', 0),
                    'goals_against': team_data.get('points_against', 0),
                    'division': self.main_gui.get_team_full_division(team_name)
                }

                conference = self.main_gui.get_team_conference(team_name)
                if conference == "Eastern":
                    eastern_teams.append(team_info)
                elif conference == "Western":
                    western_teams.append(team_info)

            # Sort each conference by points, then by goal differential
            for teams in [eastern_teams, western_teams]:
                teams.sort(key=lambda x: (
                    x['points'],
                    x['goals_for'] - x['goals_against'],
                    x['wins']
                ), reverse=True)

            # Take top 4 from each conference
            playoff_teams["Eastern"] = eastern_teams[:4]
            playoff_teams["Western"] = western_teams[:4]

        except Exception as e:
            print(f"Error determining playoff teams: {e}")

        return playoff_teams

    def _is_division_winner(self, team, conference):
        """Check if team is a division winner"""
        # This is a simplified check - you could make it more robust
        return True  # For now, assume all teams could be division winners

    def _check_week_complete(self, week):
        """Check if all games in a week are completed"""
        week_games = [g for g in self.main_gui.playoff_schedule if g.get('week') == week]
        return all(g.get('completed', False) for g in week_games)

    def _week_games_exist(self, week):
        """Check if games for a week already exist"""
        return any(g.get('week') == week for g in self.main_gui.playoff_schedule)

    def _get_conference_semifinal_winners(self, conference):
        """Get winners from conference semifinals"""
        winners = []
        for game in self.main_gui.playoff_schedule:
            if (game.get('week') == 16 and
                game.get('completed') and
                conference in game.get('round', '')):

                home_score = game.get('home_score', 0)
                away_score = game.get('away_score', 0)
                winner = game['home_team'] if home_score > away_score else game['away_team']
                winners.append(winner)
        return winners

    def _get_conference_final_winners(self):
        """Get winners from conference finals"""
        winners = []
        for game in self.main_gui.playoff_schedule:
            if (game.get('week') == 17 and game.get('completed')):
                home_score = game.get('home_score', 0)
                away_score = game.get('away_score', 0)
                winner = game['home_team'] if home_score > away_score else game['away_team']
                winners.append(winner)
        return winners

    def _get_higher_seed(self, teams):
        """Get higher seed team for home field advantage"""
        # For now, return first team (would need seeding logic)
        return teams[0]

    def _get_lower_seed(self, teams):
        """Get lower seed team"""
        return teams[1]

    def _get_playoff_date(self, week):
        """Get the date for a playoff week"""
        try:
            season_start = datetime(2025, 6, 1)
            playoff_date = season_start + timedelta(weeks=week-1)
            return playoff_date.strftime("%Y-%m-%d")
        except:
            return "2025-09-01"

    def get_playoff_bracket_text(self):
        """Generate playoff bracket text"""
        playoff_teams = self._get_playoff_teams()

        text = "PLAYOFF BRACKET\n"
        text += "=" * 50 + "\n\n"

        # Show seeding
        for conf_name, teams in playoff_teams.items():
            text += f"{conf_name.upper()} CONFERENCE:\n"
            for i, team in enumerate(teams, 1):
                text += f"  {i}. {team['name']} ({team['points']} pts)\n"
            text += "\n"

        text += "CONFERENCE SEMIFINALS (Week 16):\n"
        text += "  Eastern: 1v4, 2v3\n"
        text += "  Western: 1v4, 2v3\n\n"

        text += "CONFERENCE FINALS (Week 17):\n"
        text += "  Eastern Winner vs Eastern Winner\n"
        text += "  Western Winner vs Western Winner\n\n"

        text += "CHAMPIONSHIP (Week 18):\n"
        text += "  Eastern Champion vs Western Champion\n"

        return text
