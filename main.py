from models.player import Player
from models.team import Team
from game_schedule import generate_schedule
from season import simulate_season

# Define teams and divisions
teams_names = [
    "Buffalo Glacier", "Richmond Rebellion", "Louisville Stampede",
    "Minneapolis Chill", "Phoenix Dustrunners", "San Jose Quakebirds",
    "Toronto Ironhawks", "Montreal Sentries", "Calgary Nightwolves",
    "Spokane Tempest", "El Paso Vortex", "Atlanta Firewing"
]

divisions = {
    "East North": ["Buffalo Glacier", "Toronto Ironhawks", "Montreal Sentries"],
    "East South": ["Richmond Rebellion", "Louisville Stampede", "Atlanta Firewing"],
    "West North": ["Minneapolis Chill", "Calgary Nightwolves", "Spokane Tempest"],
    "West South": ["San Jose Quakebirds", "Phoenix Dustrunners", "El Paso Vortex"]
}

# Create Player template generator (just simple example)
def create_players(team_name):
    players = []
    positions = ['Attack', 'Attack', 'Attack', 'Midfield', 'Midfield', 'Midfield', 'Defense', 'Defense', 'Defense', 'Goalie']
    for i, pos in enumerate(positions):
        players.append(Player(
            name=f"{team_name} Player{i+1}",
            position=pos,
            shooting=70 + (i * 2) % 30,
            passing=65 + (i * 3) % 25,
            defense=50 + (i * 4) % 40,
            stamina=60 + (i * 5) % 40,
        ))
    return players

# Create Team objects with players
teams = []
for name in teams_names:
    teams.append(Team(name=name, players=create_players(name)))

# Generate schedule
schedule = generate_schedule(teams_names, divisions)

# Simulate season
simulate_season(schedule, teams)
