from typing import List, Dict, Tuple

def generate_schedule(teams: List[str], divisions: Dict[str, List[str]]) -> List[List[Tuple[str, str]]]:
    matches = []

    # Divisional matches twice (home and away)
    for division_teams in divisions.values():
        for i, home in enumerate(division_teams):
            for away in division_teams[i+1:]:
                matches.append((home, away))
                matches.append((away, home))

    # Inter-division matches once
    for i, home in enumerate(teams):
        for away in teams[i+1:]:
            same_division = any(home in div and away in div for div in divisions.values())
            if not same_division:
                matches.append((home, away))

    import random
    random.shuffle(matches)

    weeks = []
    remaining_matches = matches.copy()

    while remaining_matches:
        week_matches = []
        teams_playing = set()

        for match in remaining_matches[:]:
            home, away = match
            if home not in teams_playing and away not in teams_playing:
                week_matches.append(match)
                teams_playing.add(home)
                teams_playing.add(away)
                remaining_matches.remove(match)

        weeks.append(week_matches)

    return weeks
