import random
from datetime import datetime, timedelta
from models.team import Team

def schedule_games_efficiently(all_matchups, team_names, weeks_count=14):
    """
    Enhanced scheduling algorithm with better week utilization
    """
    print(f"\nScheduling {len(all_matchups)} games across {weeks_count} weeks...")

    # Initialize data structures
    weeks = [[] for _ in range(weeks_count)]
    team_week_schedule = {team: [False] * weeks_count for team in team_names}
    failed_games = []

    # Categorize games by type for better scheduling order
    intra_division_games = []
    inter_division_games = []
    inter_conference_games = []

    # Team division mapping for categorization
    team_divisions = {
        "Buffalo Glacier": "Eastern_North", "Toronto Ironhawks": "Eastern_North",
        "Montreal Sentries": "Eastern_North", "Boston Riptide": "Eastern_North",
        "Richmond Rebellion": "Eastern_South", "Louisville Stampede": "Eastern_South",
        "Atlanta Firewing": "Eastern_South", "Charlotte Thunder": "Eastern_South",
        "Minneapolis Chill": "Western_North", "Calgary Nightwolves": "Western_North",
        "Spokane Tempest": "Western_North", "Seattle Storm": "Western_North",
        "San Jose Quakebirds": "Western_South", "Phoenix Dustrunners": "Western_South",
        "El Paso Vortex": "Western_South", "Denver Rapids": "Western_South"
    }

    team_conferences = {
        "Buffalo Glacier": "Eastern", "Toronto Ironhawks": "Eastern",
        "Montreal Sentries": "Eastern", "Boston Riptide": "Eastern",
        "Richmond Rebellion": "Eastern", "Louisville Stampede": "Eastern",
        "Atlanta Firewing": "Eastern", "Charlotte Thunder": "Eastern",
        "Minneapolis Chill": "Western", "Calgary Nightwolves": "Western",
        "Spokane Tempest": "Western", "Seattle Storm": "Western",
        "San Jose Quakebirds": "Western", "Phoenix Dustrunners": "Western",
        "El Paso Vortex": "Western", "Denver Rapids": "Western"
    }

    # Categorize games
    for home, away in all_matchups:
        home_div = team_divisions.get(home, "")
        away_div = team_divisions.get(away, "")
        home_conf = team_conferences.get(home, "")
        away_conf = team_conferences.get(away, "")

        if home_div == away_div:
            intra_division_games.append((home, away))
        elif home_conf == away_conf:
            inter_division_games.append((home, away))
        else:
            inter_conference_games.append((home, away))

    print(f"  Categorized: {len(intra_division_games)} intra-division, {len(inter_division_games)} inter-division, {len(inter_conference_games)} inter-conference")

    def get_available_weeks(team1, team2):
        """Get weeks where both teams are available"""
        available = []
        for week in range(weeks_count):
            if (not team_week_schedule[team1][week] and
                not team_week_schedule[team2][week] and
                len(weeks[week]) < 8):  # Max 8 games per week
                available.append(week)
        return available

    def schedule_game_optimized(home, away):
        """Try to schedule a single game with optimized week selection"""
        available_weeks = get_available_weeks(home, away)

        if not available_weeks:
            return False

        # Strategy: Fill weeks more evenly - prefer weeks with fewer than 7 games
        # This helps utilize capacity better
        weeks_under_capacity = [w for w in available_weeks if len(weeks[w]) < 7]

        if weeks_under_capacity:
            # Among under-capacity weeks, choose one with most games (but still under 7)
            best_week = max(weeks_under_capacity, key=lambda w: len(weeks[w]))
        else:
            # All available weeks have 7 games, pick the first one
            best_week = available_weeks[0]

        # Schedule the game
        weeks[best_week].append((home, away))
        team_week_schedule[home][best_week] = True
        team_week_schedule[away][best_week] = True
        return True

    def force_schedule_with_swapping(home, away):
        """Try to force schedule by swapping existing games"""
        # Find weeks where at least one team is free
        candidate_weeks = []
        for week in range(weeks_count):
            if len(weeks[week]) < 8:  # Not at maximum capacity
                teams_busy = set()
                if team_week_schedule[home][week]:
                    teams_busy.add(home)
                if team_week_schedule[away][week]:
                    teams_busy.add(away)

                if len(teams_busy) <= 1:  # At most one team is busy
                    candidate_weeks.append((week, teams_busy))

        # Try to swap games to make room
        for week, busy_teams in candidate_weeks:
            if not busy_teams:
                # Both teams are free, schedule directly
                weeks[week].append((home, away))
                team_week_schedule[home][week] = True
                team_week_schedule[away][week] = True
                return True

            # One team is busy - try to move their game
            busy_team = list(busy_teams)[0]

            # Find the game involving the busy team
            for i, (game_home, game_away) in enumerate(weeks[week]):
                if busy_team in (game_home, game_away):
                    # Try to move this game to another week
                    other_team = game_away if game_home == busy_team else game_home

                    # Find alternative weeks for this game
                    alt_weeks = get_available_weeks(game_home, game_away)
                    alt_weeks = [w for w in alt_weeks if w != week]

                    if alt_weeks:
                        # Move the conflicting game
                        new_week = min(alt_weeks, key=lambda w: len(weeks[w]))

                        # Remove from current week
                        weeks[week].pop(i)
                        team_week_schedule[game_home][week] = False
                        team_week_schedule[game_away][week] = False

                        # Add to new week
                        weeks[new_week].append((game_home, game_away))
                        team_week_schedule[game_home][new_week] = True
                        team_week_schedule[game_away][new_week] = True

                        # Now schedule our target game
                        weeks[week].append((home, away))
                        team_week_schedule[home][week] = True
                        team_week_schedule[away][week] = True
                        return True

        return False

    # Schedule all games in mixed order to better distribute load
    all_games_mixed = []

    import random
    random.shuffle(inter_conference_games)
    random.shuffle(inter_division_games)
    random.shuffle(intra_division_games)

    # Interleave game types for better distribution
    max_len = max(len(inter_conference_games), len(inter_division_games), len(intra_division_games))

    for i in range(max_len):
        if i < len(inter_conference_games):
            all_games_mixed.append(("inter-conference", inter_conference_games[i]))
        if i < len(inter_division_games):
            all_games_mixed.append(("inter-division", inter_division_games[i]))
        if i < len(intra_division_games):
            all_games_mixed.append(("intra-division", intra_division_games[i]))

    # Schedule all games with optimized strategy
    print("  Using optimized scheduling strategy...")
    scheduled_count = 0

    for game_type, (home, away) in all_games_mixed:
        if schedule_game_optimized(home, away):
            scheduled_count += 1
        else:
            failed_games.append((home, away))

    print(f"    Initially scheduled {scheduled_count}/{len(all_matchups)} games")

    # Enhanced rescue phase with game swapping
    if failed_games:
        print(f"  Enhanced rescue phase for {len(failed_games)} failed games...")

        rescued_games = []
        for home, away in failed_games[:]:
            if force_schedule_with_swapping(home, away):
                rescued_games.append((home, away))

        # Remove rescued games from failed list
        for game in rescued_games:
            failed_games.remove(game)

        print(f"    Rescued {len(rescued_games)} games through swapping")

    scheduled_games = len(all_matchups) - len(failed_games)
    print(f"Successfully scheduled: {scheduled_games} out of {len(all_matchups)} games")

    if failed_games:
        print(f"Failed to schedule {len(failed_games)} games:")
        for home, away in failed_games[:5]:  # Show first 5 only
            print(f"  {home} vs {away}")
        if len(failed_games) > 5:
            print(f"  ... and {len(failed_games) - 5} more")

    return weeks, team_week_schedule, failed_games

def build_season_schedule(teams, start_date="2025-06-01"):
    """
    Build a 12-game conference schedule over 14 weeks.
    Each team plays:
    - 6 games vs division opponents (play each of 3 other teams twice - home and away)
    - 4 games vs other division in same conference (play each team once)
    - 2 games vs inter-conference opponents
    - 2 bye weeks
    Total: 12 games per team, 96 total games
    """

    # Map team names to their conference/division
    team_divisions = {
        # Eastern Conference - North Division
        "Buffalo Glacier": ("Eastern", "North"),
        "Toronto Ironhawks": ("Eastern", "North"),
        "Montreal Sentries": ("Eastern", "North"),
        "Boston Riptide": ("Eastern", "North"),
        # Eastern Conference - South Division
        "Richmond Rebellion": ("Eastern", "South"),
        "Louisville Stampede": ("Eastern", "South"),
        "Atlanta Firewing": ("Eastern", "South"),
        "Charlotte Thunder": ("Eastern", "South"),
        # Western Conference - North Division
        "Minneapolis Chill": ("Western", "North"),
        "Calgary Nightwolves": ("Western", "North"),
        "Spokane Tempest": ("Western", "North"),
        "Seattle Storm": ("Western", "North"),
        # Western Conference - South Division
        "San Jose Quakebirds": ("Western", "South"),
        "Phoenix Dustrunners": ("Western", "South"),
        "El Paso Vortex": ("Western", "South"),
        "Denver Rapids": ("Western", "South")
    }

    # Extract team names
    team_names = []
    for team in teams:
        if hasattr(team, 'name'):
            team_names.append(team.name)
        else:
            team_names.append(team)

    # Organize teams by divisions
    divisions = {
        "Eastern_North": [],
        "Eastern_South": [],
        "Western_North": [],
        "Western_South": []
    }

    for team_name in team_names:
        if team_name in team_divisions:
            conf, div = team_divisions[team_name]
            divisions[f"{conf}_{div}"].append(team_name)

    print("Team organization:")
    for div_name, div_teams in divisions.items():
        print(f"  {div_name}: {div_teams}")

    # Generate all matchups
    all_matchups = []

    # 1. Intra-division games (6 games per team)
    print("\nGenerating intra-division games...")
    intra_division_total = 0

    for div_name, div_teams in divisions.items():
        if len(div_teams) == 4:
            # Each team plays every other team in division twice (home and away)
            for i in range(4):
                for j in range(i + 1, 4):  # Only generate each unique pair once
                    # Add home and away games between this pair
                    all_matchups.append((div_teams[i], div_teams[j]))  # i home vs j away
                    all_matchups.append((div_teams[j], div_teams[i]))  # j home vs i away
                    intra_division_total += 2

            # Each team plays 3 opponents × 2 games each = 6 games per team
            print(f"  {div_name}: Added 12 intra-division games (6 per team)")

    print(f"Total intra-division games: {intra_division_total}")

    # 2. Inter-division within conference (4 games per team)
    print("\nGenerating inter-division conference games...")
    inter_division_total = 0

    # Eastern Conference: North vs South
    eastern_north = divisions["Eastern_North"]
    eastern_south = divisions["Eastern_South"]

    for team1 in eastern_north:
        for team2 in eastern_south:
            all_matchups.append((team1, team2))
            inter_division_total += 1

    # Western Conference: North vs South
    western_north = divisions["Western_North"]
    western_south = divisions["Western_South"]

    for team1 in western_north:
        for team2 in western_south:
            all_matchups.append((team1, team2))
            inter_division_total += 1

    print(f"Total inter-division games: {inter_division_total}")

    # 3. Inter-conference games (2 games per team)
    print("\nGenerating inter-conference games...")
    inter_conference_total = 0

    # Create a rotation for inter-conference matchups
    # Eastern North vs Western divisions (2 games each)
    en_matchups = [
        (eastern_north[0], western_north[0]), (eastern_north[0], western_south[0]),  # Buffalo
        (eastern_north[1], western_north[1]), (eastern_north[1], western_south[1]),  # Toronto
        (eastern_north[2], western_north[2]), (eastern_north[2], western_south[2]),  # Montreal
        (eastern_north[3], western_north[3]), (eastern_north[3], western_south[3])   # Boston
    ]

    # Eastern South vs Western divisions (2 games each)
    es_matchups = [
        (eastern_south[0], western_south[1]), (eastern_south[0], western_north[1]),  # Richmond
        (eastern_south[1], western_south[2]), (eastern_south[1], western_north[2]),  # Louisville
        (eastern_south[2], western_south[3]), (eastern_south[2], western_north[3]),  # Atlanta
        (eastern_south[3], western_south[0]), (eastern_south[3], western_north[0])   # Charlotte
    ]

    for matchup in en_matchups + es_matchups:
        all_matchups.append(matchup)
        inter_conference_total += 1

    print(f"Total inter-conference games: {inter_conference_total}")
    print(f"Each team plays 2 inter-conference opponents")

    # Verify matchup count
    team_game_count = {}
    for home, away in all_matchups:
        team_game_count[home] = team_game_count.get(home, 0) + 1
        team_game_count[away] = team_game_count.get(away, 0) + 1

    print(f"\nMatchup verification:")
    print(f"Total matchups generated: {len(all_matchups)} (should be 96)")

    all_teams_correct = True
    for team in sorted(team_names):
        count = team_game_count.get(team, 0)
        if count != 12:
            print(f"  ERROR: {team} has {count} games instead of 12!")
            all_teams_correct = False
        else:
            print(f"  {team}: {count} games ✓")

    if not all_teams_correct:
        print("ERROR: Matchup generation failed!")
        return []

    # EFFICIENT SCHEDULING using greedy approach (NOW WITH 14 WEEKS)
    weeks, team_week_schedule, failed_games = schedule_games_efficiently(all_matchups, team_names, 14)

    # Generate final schedule with dates
    schedule = []
    start = datetime.strptime(start_date, "%Y-%m-%d")

    for week_num, week_matches in enumerate(weeks):
        match_date = start + timedelta(weeks=week_num)
        for home, away in week_matches:
            schedule.append({
                "week": week_num + 1,
                "date": match_date.strftime("%Y-%m-%d"),
                "home_team": home,
                "away_team": away,
            })

    # Final verification
    final_team_count = {}
    for game in schedule:
        home = game['home_team']
        away = game['away_team']
        final_team_count[home] = final_team_count.get(home, 0) + 1
        final_team_count[away] = final_team_count.get(away, 0) + 1

    print(f"\nFinal schedule: {len(schedule)} total games across 14 weeks")
    print(f"Games per week: {[len(week) for week in weeks]}")

    # Calculate bye weeks for each team
    print(f"\nBye week analysis:")
    for team in sorted(team_names):
        bye_weeks = []
        for week in range(14):
            if not team_week_schedule[team][week]:
                bye_weeks.append(week + 1)
        print(f"  {team}: {len(bye_weeks)} bye weeks {bye_weeks}")

    print(f"\nFinal verification:")
    all_correct = True
    for team in sorted(team_names):
        count = final_team_count.get(team, 0)
        if count != 12:
            print(f"  ERROR: {team} has {count} games (should be 12)")
            all_correct = False
        else:
            print(f"  {team}: {count} games ✓")

    if all_correct:
        print("\nSUCCESS: All teams have exactly 12 games with 2 bye weeks each!")
    else:
        print("\nERROR: Schedule generation failed!")

    return schedule

def verify_schedule_balance(schedule):
    """Verify that the schedule is properly balanced"""
    team_games = {}
    team_home_games = {}
    team_away_games = {}

    for game in schedule:
        home = game['home_team']
        away = game['away_team']

        team_games[home] = team_games.get(home, 0) + 1
        team_games[away] = team_games.get(away, 0) + 1
        team_home_games[home] = team_home_games.get(home, 0) + 1
        team_away_games[away] = team_away_games.get(away, 0) + 1

    print("\nDetailed Schedule Verification:")
    print("=" * 50)
    for team in sorted(team_games.keys()):
        total = team_games.get(team, 0)
        home = team_home_games.get(team, 0)
        away = team_away_games.get(team, 0)
        print(f"{team}: {total} total ({home} home, {away} away)")

    return team_games
