from datetime import datetime, timedelta

class PlayoffSystem:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def generate_playoff_schedule(self):
        """Generate playoff bracket starting at week 15 for 14-week regular season"""
        print("Generating playoff schedule...")

        playoff_teams = self._get_playoff_teams()
        playoff_schedule = []

        # Determine home field advantage (better record gets home field)
        eastern_matchup = self._determine_home_field(playoff_teams["Eastern"])
        western_matchup = self._determine_home_field(playoff_teams["Western"])

        # Week 15: Conference Semifinals
        playoff_schedule.extend([
            {
                "week": 15,
                "date": self._get_playoff_date(15),
                "round": "Eastern Conference Semifinal",
                "home_team": eastern_matchup["home"],
                "away_team": eastern_matchup["away"],
                "home_score": None,
                "away_score": None,
                "completed": False
            },
            {
                "week": 15,
                "date": self._get_playoff_date(15),
                "round": "Western Conference Semifinal",
                "home_team": western_matchup["home"],
                "away_team": western_matchup["away"],
                "home_score": None,
                "away_score": None,
                "completed": False
            }
        ])

        # Week 16: Conference Finals (TBD teams)
        playoff_schedule.extend([
            {
                "week": 16,
                "date": self._get_playoff_date(16),
                "round": "Eastern Conference Final",
                "home_team": "TBD Eastern Winner",
                "away_team": "TBD Eastern Winner",
                "home_score": None,
                "away_score": None,
                "completed": False
            },
            {
                "week": 16,
                "date": self._get_playoff_date(16),
                "round": "Western Conference Final",
                "home_team": "TBD Western Winner",
                "away_team": "TBD Western Winner",
                "home_score": None,
                "away_score": None,
                "completed": False
            }
        ])

        # Week 17: Championship Game
        playoff_schedule.append({
            "week": 17,
            "date": self._get_playoff_date(17),
            "round": "Championship Game",
            "home_team": "TBD Eastern Champion",
            "away_team": "TBD Western Champion",
            "home_score": None,
            "away_score": None,
            "completed": False
        })

        print(f"Generated {len(playoff_schedule)} playoff games")
        return playoff_schedule

    def _get_playoff_teams(self):
        """Get division winners for playoffs (top team from each division)"""
        playoff_teams = {
            "Eastern": [],
            "Western": []
        }

        if not hasattr(self.main_gui, 'standings') or not self.main_gui.standings:
            # Fallback if no standings available
            return {
                "Eastern": ["TBD Eastern 1", "TBD Eastern 2"],
                "Western": ["TBD Western 1", "TBD Western 2"]
            }

        try:
            # Group teams by division
            divisions = {
                "Eastern North": [],
                "Eastern South": [],
                "Western North": [],
                "Western South": []
            }

            # Organize teams by division
            for team_name, team_data in self.main_gui.standings.items():
                div = team_data.get('division', 'Unknown')
                if div in divisions:
                    divisions[div].append({
                        'name': team_name,
                        'wins': team_data.get('wins', 0),
                        'losses': team_data.get('losses', 0),
                        'overtime_losses': team_data.get('overtime_losses', 0),
                        'points': team_data.get('wins', 0) * 2 + team_data.get('overtime_losses', 0),
                        'goals_for': team_data.get('points_for', 0),
                        'goals_against': team_data.get('points_against', 0)
                    })

            # Get division winners (top team in each division by points)
            for div_name, teams in divisions.items():
                if teams:
                    # Sort by points (wins * 2 + OT losses), then by goal differential
                    teams.sort(key=lambda x: (
                        x['points'],
                        x['goals_for'] - x['goals_against']
                    ), reverse=True)

                    winner = teams[0]

                    if "Eastern" in div_name:
                        playoff_teams["Eastern"].append(winner)
                    else:
                        playoff_teams["Western"].append(winner)

            # Ensure we have exactly 2 teams per conference
            if len(playoff_teams["Eastern"]) != 2:
                print(f"Warning: Eastern conference has {len(playoff_teams['Eastern'])} teams instead of 2")
            if len(playoff_teams["Western"]) != 2:
                print(f"Warning: Western conference has {len(playoff_teams['Western'])} teams instead of 2")

        except Exception as e:
            print(f"Error determining playoff teams: {e}")
            # Fallback to placeholder teams
            return {
                "Eastern": ["TBD Eastern 1", "TBD Eastern 2"],
                "Western": ["TBD Western 1", "TBD Western 2"]
            }

        return playoff_teams

    def _determine_home_field(self, conference_teams):
        """Determine home field advantage between two teams"""
        if len(conference_teams) != 2:
            return {"home": "TBD", "away": "TBD"}

        team1, team2 = conference_teams

        # Home field goes to team with better record
        if team1['points'] > team2['points']:
            return {"home": team1['name'], "away": team2['name']}
        elif team2['points'] > team1['points']:
            return {"home": team2['name'], "away": team1['name']}
        else:
            # Tie-breaker: goal differential
            team1_diff = team1['goals_for'] - team1['goals_against']
            team2_diff = team2['goals_for'] - team2['goals_against']

            if team1_diff > team2_diff:
                return {"home": team1['name'], "away": team2['name']}
            else:
                return {"home": team2['name'], "away": team1['name']}

    def _get_playoff_date(self, week):
        """Get the date for a playoff week"""
        try:
            # Assume regular season starts June 1, 2025
            season_start = datetime(2025, 6, 1)
            playoff_date = season_start + timedelta(weeks=week-1)
            return playoff_date.strftime("%Y-%m-%d")
        except:
            return "2025-09-01"  # Fallback date

    def get_playoff_bracket_text(self):
        """Generate text representation of playoff bracket"""
        playoff_teams = self._get_playoff_teams()

        bracket_text = "PLAYOFF BRACKET\n"
        bracket_text += "=" * 50 + "\n\n"
        bracket_text += "CONFERENCE SEMIFINALS (Week 15)\n"
        bracket_text += "-" * 30 + "\n"

        # Eastern Conference
        if len(playoff_teams["Eastern"]) >= 2:
            bracket_text += f"Eastern: {playoff_teams['Eastern'][0]['name']} vs {playoff_teams['Eastern'][1]['name']}\n"
        else:
            bracket_text += "Eastern: TBD vs TBD\n"

        # Western Conference
        if len(playoff_teams["Western"]) >= 2:
            bracket_text += f"Western: {playoff_teams['Western'][0]['name']} vs {playoff_teams['Western'][1]['name']}\n"
        else:
            bracket_text += "Western: TBD vs TBD\n"

        bracket_text += "\nCONFERENCE FINALS (Week 16)\n"
        bracket_text += "-" * 30 + "\n"
        bracket_text += "Eastern Winner vs Western Winner\n\n"

        bracket_text += "CHAMPIONSHIP (Week 17)\n"
        bracket_text += "-" * 30 + "\n"
        bracket_text += "Conference Champions\n"

        return bracket_text

    def update_playoff_bracket(self, completed_games):
        """Update playoff bracket based on completed games"""
        # This method would be called to update TBD teams after games are completed
        # Implementation would depend on how you want to handle advancing teams
        pass
