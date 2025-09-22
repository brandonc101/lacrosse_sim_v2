class PlayoffSystem:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def get_conference_from_division(self, division):
        """Get conference name from division"""
        if division.startswith("Eastern"):
            return "Eastern"
        elif division.startswith("Western"):
            return "Western"
        return "Unknown"

    def calculate_conference_standings(self):
        """Calculate standings within each conference"""
        conferences = {"Eastern": [], "Western": []}

        for team_name, stats in self.main_gui.standings.items():
            division = stats.get('division', 'Unknown')
            conference = self.get_conference_from_division(division)

            if conference in conferences:
                team_data = {
                    'name': team_name,
                    'division': division,
                    'conference': conference,
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'overtime_losses': stats.get('overtime_losses', 0),
                    'points_for': stats['points_for'],
                    'points_against': stats['points_against'],
                    'games_played': stats['games_played'],
                    'win_pct': stats['wins'] / max(1, stats['games_played']),
                    'point_diff': stats['points_for'] - stats['points_against']
                }
                conferences[conference].append(team_data)

        # Sort each conference by win percentage, then point differential
        for conference in conferences:
            conferences[conference].sort(
                key=lambda x: (x['win_pct'], x['point_diff']),
                reverse=True
            )

        return conferences

    def determine_playoff_teams(self):
        """Determine the 8 playoff teams (top 2 from each division)"""
        playoff_teams = []

        # Group teams by division
        division_teams = {}
        for team_name, stats in self.main_gui.standings.items():
            division = stats.get('division', 'Unknown')
            if division not in division_teams:
                division_teams[division] = []

            team_data = {
                'name': team_name,
                'division': division,
                'wins': stats['wins'],
                'losses': stats['losses'],
                'games_played': stats['games_played'],
                'win_pct': stats['wins'] / max(1, stats['games_played']),
                'point_diff': stats['points_for'] - stats['points_against']
            }
            division_teams[division].append(team_data)

        # Get top 2 from each division
        for division, teams in division_teams.items():
            teams.sort(key=lambda x: (x['win_pct'], x['point_diff']), reverse=True)
            playoff_teams.extend(teams[:2])  # Top 2 from each division

        return playoff_teams

    def create_conference_playoffs(self, conference_teams):
        """Create playoff bracket for one conference (4 teams)"""
        # Sort by overall record within conference
        sorted_teams = sorted(conference_teams,
                            key=lambda x: (x['win_pct'], x['point_diff']),
                            reverse=True)

        if len(sorted_teams) < 4:
            return []

        # Conference Semifinals: 1 vs 4, 2 vs 3
        semifinals = [
            {
                'round': 'Conference Semifinal',
                'home_team': sorted_teams[0]['name'],  # 1st seed
                'away_team': sorted_teams[3]['name'],  # 4th seed
                'home_seed': 1,
                'away_seed': 4
            },
            {
                'round': 'Conference Semifinal',
                'home_team': sorted_teams[1]['name'],  # 2nd seed
                'away_team': sorted_teams[2]['name'],  # 3rd seed
                'home_seed': 2,
                'away_seed': 3
            }
        ]

        return semifinals

    def generate_playoff_schedule(self):
        """Generate the complete 3-week playoff schedule"""
        playoff_teams = self.determine_playoff_teams()

        # Separate into conferences
        eastern_teams = [t for t in playoff_teams if self.get_conference_from_division(t['division']) == 'Eastern']
        western_teams = [t for t in playoff_teams if self.get_conference_from_division(t['division']) == 'Western']

        playoff_schedule = []

        # Week 14: Conference Semifinals
        eastern_semis = self.create_conference_playoffs(eastern_teams)
        western_semis = self.create_conference_playoffs(western_teams)

        week_14_games = []
        for game in eastern_semis + western_semis:
            week_14_games.append({
                'week': 14,
                'round': game['round'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'home_seed': game['home_seed'],
                'away_seed': game['away_seed'],
                'conference': 'Eastern' if game in eastern_semis else 'Western',
                'home_score': None,
                'away_score': None,
                'completed': False
            })

        playoff_schedule.extend(week_14_games)

        # Week 15: Conference Finals (placeholders - will be filled after week 14)
        week_15_games = [
            {
                'week': 15,
                'round': 'Eastern Conference Final',
                'home_team': 'TBD (Higher seed from Eastern Semis)',
                'away_team': 'TBD (Lower seed from Eastern Semis)',
                'conference': 'Eastern',
                'home_score': None,
                'away_score': None,
                'completed': False
            },
            {
                'week': 15,
                'round': 'Western Conference Final',
                'home_team': 'TBD (Higher seed from Western Semis)',
                'away_team': 'TBD (Lower seed from Western Semis)',
                'conference': 'Western',
                'home_score': None,
                'away_score': None,
                'completed': False
            }
        ]

        playoff_schedule.extend(week_15_games)

        # Week 16: Championship Final
        week_16_games = [
            {
                'week': 16,
                'round': 'Championship Final',
                'home_team': 'TBD (Eastern Conference Champion)',
                'away_team': 'TBD (Western Conference Champion)',
                'conference': 'Championship',
                'home_score': None,
                'away_score': None,
                'completed': False
            }
        ]

        playoff_schedule.extend(week_16_games)

        return playoff_schedule

    def update_playoff_bracket(self, completed_week):
        """Update playoff bracket after completing a week"""
        if completed_week == 14:
            # Update Week 15 games based on Week 14 results
            self._update_conference_finals()
        elif completed_week == 15:
            # Update Week 16 game based on Week 15 results
            self._update_championship()

    def _update_conference_finals(self):
        """Update conference finals after semifinals"""
        # Get Week 14 results
        week_14_games = [g for g in self.main_gui.playoff_schedule if g['week'] == 14]

        eastern_winners = []
        western_winners = []

        for game in week_14_games:
            if game['completed']:
                winner = game['home_team'] if game['home_score'] > game['away_score'] else game['away_team']
                winner_seed = game['home_seed'] if game['home_score'] > game['away_score'] else game['away_seed']

                if game['conference'] == 'Eastern':
                    eastern_winners.append({'name': winner, 'seed': winner_seed})
                else:
                    western_winners.append({'name': winner, 'seed': winner_seed})

        # Update Week 15 games
        week_15_games = [g for g in self.main_gui.playoff_schedule if g['week'] == 15]

        if len(eastern_winners) == 2:
            eastern_winners.sort(key=lambda x: x['seed'])  # Lower seed = higher seed
            eastern_final = next(g for g in week_15_games if g['conference'] == 'Eastern')
            eastern_final['home_team'] = eastern_winners[0]['name']  # Higher seed gets home
            eastern_final['away_team'] = eastern_winners[1]['name']

        if len(western_winners) == 2:
            western_winners.sort(key=lambda x: x['seed'])
            western_final = next(g for g in week_15_games if g['conference'] == 'Western')
            western_final['home_team'] = western_winners[0]['name']
            western_final['away_team'] = western_winners[1]['name']

    def _update_championship(self):
        """Update championship game after conference finals"""
        week_15_games = [g for g in self.main_gui.playoff_schedule if g['week'] == 15 and g['completed']]

        if len(week_15_games) == 2:
            eastern_champ = None
            western_champ = None

            for game in week_15_games:
                winner = game['home_team'] if game['home_score'] > game['away_score'] else game['away_team']
                if game['conference'] == 'Eastern':
                    eastern_champ = winner
                else:
                    western_champ = winner

            if eastern_champ and western_champ:
                championship = next(g for g in self.main_gui.playoff_schedule if g['week'] == 16)
                championship['home_team'] = eastern_champ  # Eastern champ gets home field
                championship['away_team'] = western_champ
