import random
from typing import List
from models.player import Player
from models.team import Team

class MatchResult:
    def __init__(self, home_team: Team, away_team: Team, home_score: int, away_score: int,
                 home_shots: int, away_shots: int, home_saves: int, away_saves: int,
                 overtime: bool = False):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score
        self.home_shots = home_shots
        self.away_shots = away_shots
        self.home_saves = home_saves
        self.away_saves = away_saves
        self.overtime = overtime

def weighted_random_player(players: List[Player], roles: List[str]) -> Player:
    candidates = [p for p in players if p.position in roles]
    if not candidates:
        candidates = players[:]
    weights = []
    for p in candidates:
        base_weight = p.shooting * (p.stamina / 100)
        # Apply big penalty if goalie, e.g. multiply by 0.05 (5% chance relative to others)
        if p.position == "Goalie":
            base_weight *= 0.05
        weights.append(base_weight)

    total_weight = sum(weights)
    if total_weight == 0:
        return random.choice(candidates)
    rnd = random.uniform(0, total_weight)
    upto = 0
    for p, w in zip(candidates, weights):
        if upto + w >= rnd:
            return p
        upto += w
    return candidates[-1]

def weighted_random_assister(players: List[Player], exclude_player: Player) -> Player:
    # Allow all but exclude the shooter
    candidates = [p for p in players if p != exclude_player]
    weights = []
    for p in candidates:
        base_weight = p.passing * (p.stamina / 100)
        if p.position == "Goalie":
            base_weight *= 0.05  # 5% chance to assist relative to others
        weights.append(base_weight)

    total_weight = sum(weights)
    if total_weight == 0:
        return random.choice(candidates)
    rnd = random.uniform(0, total_weight)
    upto = 0
    for p, w in zip(candidates, weights):
        if upto + w >= rnd:
            return p
        upto += w
    return candidates[-1]

def team_shooting_accuracy(team: Team) -> float:
    shooters = [p for p in team.players if p.position in ("Attack", "Midfield")]
    avg_shooting = sum(p.shooting for p in shooters) / max(len(shooters), 1)
    defenders = [p for p in team.players if p.position == "Defense"]
    avg_defense = sum(p.defense for p in defenders) / max(len(defenders), 1)
    base_accuracy = 0.28
    accuracy = base_accuracy * (avg_shooting / 100) * (1.0 - avg_defense / 150)
    return max(0.15, min(accuracy, 0.40))

def simulate_match(home_team: Team, away_team: Team) -> MatchResult:
    avg_shots = 43
    home_shots = max(30, int(random.gauss(avg_shots, 5)))
    away_shots = max(30, int(random.gauss(avg_shots, 5)))

    home_accuracy = team_shooting_accuracy(home_team)
    away_accuracy = team_shooting_accuracy(away_team)

    home_goals = 0
    away_goals = 0

    # Reset match stats for players before the match starts
    for player in home_team.players + away_team.players:
        player.goals_match = 0
        player.assists_match = 0
        player.saves_match = 0

    for _ in range(home_shots):
        if random.random() < home_accuracy:
            home_goals += 1
            scorer = weighted_random_player(home_team.players, ["Attack", "Midfield"])
            scorer.goals += 1
            scorer.goals_match += 1
            assister = weighted_random_assister(home_team.players, scorer)
            if assister:
                assister.assists += 1
                assister.assists_match += 1

    for _ in range(away_shots):
        if random.random() < away_accuracy:
            away_goals += 1
            scorer = weighted_random_player(away_team.players, ["Attack", "Midfield"])
            scorer.goals += 1
            scorer.goals_match += 1
            assister = weighted_random_assister(away_team.players, scorer)
            if assister:
                assister.assists += 1
                assister.assists_match += 1

    home_saves = home_shots - home_goals
    away_saves = away_shots - away_goals

    def assign_saves(team: Team, saves: int):
        goalies = [p for p in team.players if p.position == "Goalie"]
        if not goalies:
            return
        weights = [p.defense * (p.stamina / 100) for p in goalies]
        total = sum(weights)
        if total == 0:
            equal_save = saves // len(goalies)
            for p in goalies:
                p.saves += equal_save
                p.saves_match += equal_save
            return
        for p, w in zip(goalies, weights):
            assigned = int(saves * (w / total))
            p.saves += assigned
            p.saves_match += assigned

    assign_saves(home_team, home_saves)
    assign_saves(away_team, away_saves)

    home_team.goals_for += home_goals
    home_team.goals_against += away_goals
    away_team.goals_for += away_goals
    away_team.goals_against += home_goals

    overtime = False

    if home_goals == away_goals:
        # Overtime simulation - sudden death until winner scores
        overtime = True
        while True:
            for offense_team, defense_team in [(home_team, away_team), (away_team, home_team)]:
                if random.random() < 0.5:  # 50% chance to get shot in OT
                    scorer = weighted_random_player(offense_team.players, ["Attack", "Midfield"])
                    ot_accuracy = team_shooting_accuracy(offense_team) * 0.8  # slightly lower accuracy in OT
                    if random.random() < ot_accuracy:
                        if offense_team == home_team:
                            home_goals += 1
                        else:
                            away_goals += 1
                        scorer.goals += 1
                        scorer.goals_match += 1
                        # Winner is offense_team, loser is defense_team
                        if offense_team == home_team:
                            home_team.wins += 1
                            away_team.overtime_losses += 1
                        else:
                            away_team.wins += 1
                            home_team.overtime_losses += 1

                        # Update points based on new rules
                        home_team.points = (home_team.wins * 2) + (home_team.overtime_losses * 1)
                        away_team.points = (away_team.wins * 2) + (away_team.overtime_losses * 1)
                        return MatchResult(home_team, away_team, home_goals, away_goals,
                                           home_shots, away_shots, home_saves, away_saves, overtime)

    # No OT, determine win/loss normally
    if not overtime:
        if home_goals > away_goals:
            home_team.wins += 1
            away_team.losses += 1
        elif away_goals > home_goals:
            away_team.wins += 1
            home_team.losses += 1

    # Update points for non-OT games
    home_team.points = (home_team.wins * 2) + (home_team.overtime_losses * 1)
    away_team.points = (away_team.wins * 2) + (away_team.overtime_losses * 1)

    return MatchResult(home_team, away_team, home_goals, away_goals, home_shots, away_shots, home_saves, away_saves, overtime)
