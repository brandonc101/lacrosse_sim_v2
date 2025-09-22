import random
from datetime import datetime, timedelta
from models.team import Team

def schedule_games_with_backtracking(all_matchups, team_names, weeks_count=12):
    """
    Advanced constraint satisfaction scheduling with full backtracking
    """
    print(f"\nScheduling {len(all_matchups)} games across {weeks_count} weeks...")

    # Initialize data structures
    weeks = [[] for _ in range(weeks_count)]
    team_week_schedule = {team: [False] * weeks_count for team in team_names}

    def is_valid_assignment(game_idx, week):
        """Check if assigning game at game_idx to week is valid"""
        home, away = all_matchups[game_idx]

        # Check if both teams are available
        if team_week_schedule[home][week] or team_week_schedule[away][week]:
            return False

        # Check week capacity (max 8 games per week)
        if len(weeks[week]) >= 8:
            return False

        return True

    def assign_game(game_idx, week):
        """Assign game to week"""
        home, away = all_matchups[game_idx]
        weeks[week].append((home, away))
        team_week_schedule[home][week] = True
        team_week_schedule[away][week] = True

    def unassign_game(game_idx, week):
        """Remove game from week"""
        home, away = all_matchups[game_idx]
        weeks[week].remove((home, away))
        team_week_schedule[home][week] = False
        team_week_schedule[away][week] = False

    def get_game_flexibility(game_idx):
        """Count how many weeks this game could be assigned to"""
        count = 0
        for week in range(weeks_count):
            if is_valid_assignment(game_idx, week):
                count += 1
        return count

    def backtrack(game_idx):
        """Recursive backtracking to assign all games"""
        if game_idx >= len(all_matchups):
            return True  # All games assigned successfully

        # Get current game flexibility and sort weeks by preference
        available_weeks = []
        for week in range(weeks_count):
            if is_valid_assignment(game_idx, week):
                # Prefer weeks with fewer games (load balancing)
                available_weeks.append((len(weeks[week]), week))

        # Sort by number of games in week (prefer less loaded weeks)
        available_weeks.sort()

        for _, week in available_weeks:
            assign_game(game_idx, week)

            if backtrack(game_idx + 1):
                return True

            unassign_game(game_idx, week)

        return False  # This assignment doesn't work

    # Sort games by constraint (least flexible first)
    print("  Analyzing game constraints...")
    game_flexibility = [(get_game_flexibility(i), i) for i in range(len(all_matchups))]
    game_flexibility.sort()  # Most constrained games first

    # Reorder matchups based on constraint level
    ordered_matchups = [all_matchups[idx] for _, idx in game_flexibility]
    all_matchups[:] = ordered_matchups

    print(f"  Game flexibility range: {game_flexibility[0][0]} to {game_flexibility[-1][0]} available weeks")

    # Attempt backtracking solution
    print("  Attempting constraint satisfaction with backtracking...")
    success = backtrack(0)

    scheduled_games = sum(len(week) for week in weeks)
    failed_games = []

    if not success:
        print(f"  Backtracking failed to find complete solution")
        # Identify which games couldn't be scheduled
        scheduled_set = set()
        for week in weeks:
            scheduled_set.update(week)

        for matchup in all_matchups:
            if matchup not in scheduled_set:
                failed_games.append(matchup)

    print(f"Successfully scheduled: {scheduled_games} out of {len(all_matchups)} games")

    if failed_games:
        print(f"Failed to schedule {len(failed_games)} games:")
        for home, away in failed_games:
            print(f"  {home} vs {away}")

    return weeks, team_week_schedule, failed_games

def build_season_schedule(teams, start_date="2025-06-01"):
    """
    Build a 10-game conference-only schedule over 12 weeks.
    Each team plays:
    - 6 games vs division opponents (play each of 3 other teams twice - home and away)
    - 4 games vs other division in same conference (play each team once)
    - 2 bye weeks
    Total: 10 games per team, 80 total games
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
    print("NO inter-conference games - staying within conferences only")

    # Verify matchup count
    team_game_count = {}
    for home, away in all_matchups:
        team_game_count[home] = team_game_count.get(home, 0) + 1
        team_game_count[away] = team_game_count.get(away, 0) + 1

    print(f"\nMatchup verification:")
    print(f"Total matchups generated: {len(all_matchups)} (should be 80)")

    all_teams_correct = True
    for team in sorted(team_names):
        count = team_game_count.get(team, 0)
        if count != 10:
            print(f"  ERROR: {team} has {count} games instead of 10!")
            all_teams_correct = False
        else:
            print(f"  {team}: {count} games ✓")

    if not all_teams_correct:
        print("ERROR: Matchup generation failed!")
        return []

    # ADVANCED SCHEDULING using backtracking constraint satisfaction
    weeks, team_week_schedule, failed_games = schedule_games_with_backtracking(all_matchups, team_names, 12)

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

    print(f"\nFinal schedule: {len(schedule)} total games across 12 weeks")
    print(f"Games per week: {[len(week) for week in weeks]}")

    # Calculate bye weeks for each team
    print(f"\nBye week analysis:")
    for team in sorted(team_names):
        bye_weeks = []
        for week in range(12):
            if not team_week_schedule[team][week]:
                bye_weeks.append(week + 1)
        print(f"  {team}: {len(bye_weeks)} bye weeks {bye_weeks}")

    print(f"\nFinal verification:")
    all_correct = True
    for team in sorted(team_names):
        count = final_team_count.get(team, 0)
        if count != 10:
            print(f"  ERROR: {team} has {count} games (should be 10)")
            all_correct = False
        else:
            print(f"  {team}: {count} games ✓")

    if all_correct:
        print("\nSUCCESS: All teams have exactly 10 games with 2 bye weeks each!")
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
