from dataclasses import dataclass
from .team import Team
import random

@dataclass
class MatchResult:
    home_team: Team
    away_team: Team
    home_score: int
    away_score: int

def weighted_choice(players, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for player, weight in zip(players, weights):
        if upto + weight >= r:
            return player
        upto += weight
    return players[-1]

def simulate_match(home: Team, away: Team) -> MatchResult:
    def team_offense(team: Team) -> int:
        return sum(p.shooting + p.passing for p in team.players if p.position in ['Attack', 'Midfield'])

    def team_defense(team: Team) -> int:
        return sum(p.defense + p.stamina for p in team.players if p.position in ['Defense', 'Goalie'])

    home_offense = team_offense(home)
    away_offense = team_offense(away)
    home_defense = team_defense(home)
    away_defense = team_defense(away)

    home_goals = max(0, int((home_offense / (away_defense + 1)) * random.uniform(0.5, 1.5)))
    away_goals = max(0, int((away_offense / (home_defense + 1)) * random.uniform(0.5, 1.5)))

    home.goals_for += home_goals
    home.goals_against += away_goals
    away.goals_for += away_goals
    away.goals_against += home_goals

    if home_goals > away_goals:
        home.wins += 1
        away.losses += 1
    elif away_goals > home_goals:
        away.wins += 1
        home.losses += 1
    else:
        home.draws += 1
        away.draws += 1

    def assign_goals_and_assists(team: Team, goals: int):
        eligible_players = [p for p in team.players if p.position in ['Attack', 'Midfield']]
        if not eligible_players:
            return

        scorer_weights = []
        for p in eligible_players:
            base_weight = (p.shooting * 0.7 + p.passing * 0.3)
            if p.position == 'Attack':
                base_weight *= 1.2
            scorer_weights.append(base_weight)

        assister_weights = []
        for p in eligible_players:
            base_weight = (p.passing * 0.6 + p.stamina * 0.4)
            if p.position == 'Midfield':
                base_weight *= 1.2
            assister_weights.append(base_weight)

        for _ in range(goals):
            scorer = weighted_choice(eligible_players, scorer_weights)
            assister_candidates = [p for p in eligible_players if p != scorer]
            assister_weights_candidates = [assister_weights[eligible_players.index(p)] for p in assister_candidates]

            assister = weighted_choice(assister_candidates, assister_weights_candidates) if assister_candidates else None

            scorer.goals += 1
            if assister:
                assister.assists += 1

    assign_goals_and_assists(home, home_goals)
    assign_goals_and_assists(away, away_goals)

    # Goalie stats
    def update_goalie_stats(team: Team, goals_allowed: int, opponent_attack_strength: int):
        goalies = [p for p in team.players if p.position == "Goalie"]
        if not goalies:
            return
        goalie = goalies[0]  # assume one goalie
        estimated_shots_faced = int(opponent_attack_strength / 10 * random.uniform(0.8, 1.2))
        goalie.saves += max(0, estimated_shots_faced - goals_allowed)

    update_goalie_stats(home, away_goals, away_offense)
    update_goalie_stats(away, home_goals, home_offense)

        # Player of the match (based on goals, assists, saves)
    candidates = home.players + away.players
    scores = []
    for p in candidates:
        score = p.goals * 4 + p.assists * 3
        if p.position == "Goalie":
            score += p.saves * 0.5
        scores.append(score)

    max_score = max(scores)
    top_players = [p for p, s in zip(candidates, scores) if s == max_score]
    selected = random.choice(top_players)
    selected.player_of_match += 1

    return MatchResult(home, away, home_goals, away_goals)
