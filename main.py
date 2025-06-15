from models.player import Player
from models.team import Team
from models.match import simulate_match

# Create players
p1 = Player(name="Alice", position="Attack", shooting=85, passing=70, defense=40, stamina=80)
p2 = Player(name="Bob", position="Midfield", shooting=70, passing=80, defense=50, stamina=85)
p3 = Player(name="Charlie", position="Defense", shooting=40, passing=50, defense=80, stamina=75)
p4 = Player(name="Derek", position="Goalie", shooting=30, passing=40, defense=85, stamina=70)

# Create teams
team1 = Team(name="East Eagles", players=[p1, p2, p3, p4])
team2 = Team(name="West Wolves", players=[p1, p2, p3, p4])  # Duplicate players just for example

# Simulate match
result = simulate_match(team1, team2)

print(f"{result.home_team.name} {result.home_score} - {result.away_score} {result.away_team.name}")
for player in team1.players + team2.players:
    print(f"{player.name} ({player.position}): Goals {player.goals}, Assists {player.assists}")
