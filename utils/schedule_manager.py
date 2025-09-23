from datetime import datetime, timedelta

class ScheduleManager:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def generate_schedule(self):
        """Generate schedule using the advanced scheduling system"""
        try:
            from models.schedule import build_season_schedule
            temp_teams = self._create_temp_teams()
            schedule_data = build_season_schedule(temp_teams)
            self._add_missing_fields(schedule_data)
            # print(f"Generated schedule with {len(schedule_data)} games")
            return schedule_data

        except ImportError:
            print("Advanced scheduler not found, falling back to basic scheduler")
            return self._fallback_schedule()

    def _create_temp_teams(self):
        """Create team objects for scheduler"""
        temp_teams = []
        for team_name in self.main_gui.teams_names:
            team_obj = type('Team', (), {
                'name': team_name,
                'division': self._get_team_division(team_name)
            })()
            temp_teams.append(team_obj)
        return temp_teams

    def _add_missing_fields(self, schedule_data):
        """Add missing fields to schedule data"""
        for game in schedule_data:
            if 'completed' not in game:
                game['completed'] = False
            if 'home_score' not in game:
                game['home_score'] = None
            if 'away_score' not in game:
                game['away_score'] = None

    def _get_team_division(self, team_name):
        """Get division for a team"""
        for div_name, teams in self.main_gui.divisions.items():
            if team_name in teams:
                return div_name
        return "Unknown"

    def _fallback_schedule(self):
        """Fallback schedule generation"""
        from game_schedule import generate_schedule
        raw_schedule = generate_schedule(self.main_gui.teams_names, self.main_gui.divisions)
        return self._convert_basic_schedule_format(raw_schedule)

    def _convert_basic_schedule_format(self, raw_schedule):
        """Convert basic schedule format"""
        converted_schedule = []
        start_date = datetime(2025, 6, 1)

        for week_num, week_games in enumerate(raw_schedule, 1):
            game_date = start_date + timedelta(weeks=week_num-1)
            for home_team, away_team in week_games:
                converted_schedule.append({
                    'week': week_num, 'date': game_date.strftime("%Y-%m-%d"),
                    'home_team': home_team, 'away_team': away_team,
                    'home_score': None, 'away_score': None, 'completed': False
                })
        return converted_schedule
