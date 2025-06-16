from typing import List
from models import team, player
from models.match import simulate_match
import csv
from collections import defaultdict

def simulate_season(schedule: List[List[tuple]], teams: List[team]) -> None:
    team_map = {team.name: team for team in teams}
    weekly_leaders = defaultdict(list)

    for week_num, week in enumerate(schedule, 1):
        print(f"=== Week {week_num} ===")
        for home_name, away_name in week:
            if home_name not in team_map or away_name not in team_map:
                raise ValueError(f"Team not found: {home_name} or {away_name}")
            home = team_map[home_name]
            away = team_map[away_name]
            result = simulate_match(home, away)
            print(f"{result.home_team.name} {result.home_score} - {result.away_score} {result.away_team.name}")

            # Track player impact scores for weekly leaders
            match_players = home.players + away.players
            for p in match_players:
                impact_score = p.goals * 4 + p.assists * 3
                if p.position == "Goalie":
                    impact_score += p.saves * 0.5
                if impact_score > 0:
                    weekly_leaders[week_num].append((p, impact_score))
        print()

    print("=== Final Standings ===")
    standings = sorted(teams, key=lambda t: (t.points, t.goals_for - t.goals_against), reverse=True)
    print(f"{'Pos':<3} {'Team':<20} {'W':<3} {'OTL':<4} {'L':<3} {'GF':<4} {'GA':<4} {'Pts':<4}")
    for i, team in enumerate(standings, 1):
        print(f"{i:<3} {team.name:<20} {team.wins:<3} {team.overtime_losses:<4} {team.losses:<3} {team.goals_for:<4} {team.goals_against:<4} {team.points:<4}")

    # === Post-Season Stats ===
    print("\n=== Player Stats ===")
    all_players = []
    for team in teams:
        all_players.extend(team.players)

    all_players.sort(key=lambda p: (p.goals, p.assists, p.saves), reverse=True)

    print(f"{'Player':<25} {'Team':<20} {'Goals':<6} {'Assists':<8} {'Saves':<6} {'POM'}")
    for player in all_players:
        if player.goals > 0 or player.assists > 0 or player.saves > 0 or player.player_of_match > 0:
            team_name = next((team.name for team in teams if player in team.players), "Unknown")
            print(f"{player.name:<25} {team_name:<20} {player.goals:<6} {player.assists:<8} {player.saves:<6} {player.player_of_match}")

    # === Export to CSV ===
    export_player_stats_csv(all_players, teams)

    # === MVP Top 10 ===
    all_players.sort(key=lambda p: (p.goals * 4 + p.assists * 3 + p.saves * 0.5 + p.player_of_match * 5), reverse=True)
    print("\n=== Top 10 Players (MVP Candidates) ===")
    for i, player in enumerate(all_players[:10], 1):
        team_name = next((team.name for team in teams if player in team.players), "Unknown")
        score = player.goals * 4 + player.assists * 3 + player.saves * 0.5 + player.player_of_match * 5
        print(f"{i}. {player.name} ({team_name}) - {score:.1f} pts [G:{player.goals}, A:{player.assists}, Sv:{player.saves}, POM:{player.player_of_match}]")

    # === Weekly Leaders ===
    print("\n=== Weekly Top Performers ===")
    for week in sorted(weekly_leaders.keys()):
        print(f"\nWeek {week}:")
        week_scores = sorted(weekly_leaders[week], key=lambda x: x[1], reverse=True)
        shown = set()
        count = 0
        for player, score in week_scores:
            if player.name in shown:
                continue
            team_name = next((team.name for team in teams if player in team.players), "Unknown")
            print(f" - {player.name} ({team_name}) | Score: {score:.1f} [G:{player.goals}, A:{player.assists}, Sv:{player.saves}]")
            shown.add(player.name)
            count += 1
            if count >= 3:
                break


def export_player_stats_csv(players: List[player], teams: List[team], filename="player_stats.csv"):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["Player", "Team", "Position", "Goals", "Assists", "Saves", "Player of Match"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for player in players:
            team_name = next((team.name for team in teams if player in team.players), "Unknown")
            writer.writerow({
                "Player": player.name,
                "Team": team_name,
                "Position": player.position,
                "Goals": player.goals,
                "Assists": player.assists,
                "Saves": player.saves,
                "Player of Match": player.player_of_match,
            })
