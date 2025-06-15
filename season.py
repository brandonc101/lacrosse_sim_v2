from typing import List
from models.team import Team
from models.match import simulate_match

def simulate_season(schedule: List[List[tuple]], teams: List[Team]) -> None:
    team_map = {team.name: team for team in teams}

    for week_num, week in enumerate(schedule, 1):
        print(f"=== Week {week_num} ===")
        for home_name, away_name in week:
            home = team_map[home_name]
            away = team_map[away_name]
            result = simulate_match(home, away)
            print(f"{result.home_team.name} {result.home_score} - {result.away_score} {result.away_team.name}")
        print()

    print("=== Final Standings ===")
    standings = sorted(teams, key=lambda t: (t.wins * 3 + t.draws, t.goals_for - t.goals_against), reverse=True)
    for i, team in enumerate(standings, 1):
        print(f"{i}. {team.name} W:{team.wins} D:{team.draws} L:{team.losses} GF:{team.goals_for} GA:{team.goals_against}")
