import random
from datetime import datetime, timedelta
from models.team import Team

def build_season_schedule(teams, start_date="2025-06-01"):
    # Group teams by division
    divisions = {}
    for team in teams:
        divisions.setdefault(team.division, []).append(team)

    # Build matchups
    matchups = set()

    for division_teams in divisions.values():
        for i, team_a in enumerate(division_teams):
            for j, team_b in enumerate(division_teams):
                if i < j:
                    matchups.add((team_a.name, team_b.name))
                    matchups.add((team_b.name, team_a.name))  # Play twice in-division

    for i, team_a in enumerate(teams):
        for j, team_b in enumerate(teams):
            if i < j and (team_a.name, team_b.name) not in matchups and team_a.division != team_b.division:
                matchups.add((team_a.name, team_b.name))  # Play once outside division

    matchups = list(matchups)
    random.shuffle(matchups)

    # Schedule over 13 weeks (1 match per team per week)
    weeks = [[] for _ in range(13)]
    scheduled_teams_per_week = [set() for _ in range(13)]

    for home, away in matchups:
        for week in range(13):
            if home not in scheduled_teams_per_week[week] and away not in scheduled_teams_per_week[week]:
                weeks[week].append((home, away))
                scheduled_teams_per_week[week].add(home)
                scheduled_teams_per_week[week].add(away)
                break

    # Attach calendar dates
    schedule = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    for i, week_matches in enumerate(weeks):
        match_date = start + timedelta(weeks=i)
        for home, away in week_matches:
            schedule.append({
                "week": i + 1,
                "date": match_date.strftime("%Y-%m-%d"),
                "home": home,
                "away": away,
            })

    return schedule
