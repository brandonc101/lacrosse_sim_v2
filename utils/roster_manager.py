import os
import json
from models.player import Player
from models.team import Team

def player_to_dict(player: Player):
    return {
        "name": player.name,
        "position": player.position,
        "shooting": player.shooting,
        "passing": player.passing,
        "defense": player.defense,
        "stamina": player.stamina,
    }

def dict_to_player(data) -> Player:
    return Player(
        name=data["name"],
        position=data["position"],
        shooting=data["shooting"],
        passing=data["passing"],
        defense=data["defense"],
        stamina=data["stamina"],
    )

def save_team_to_file(team: Team, folder="teams_data"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{team.name}.json")
    with open(path, "w") as f:
        json.dump([player_to_dict(p) for p in team.players], f, indent=2)

def load_team_from_file(name: str, folder="teams_data") -> Team | None:
    path = os.path.join(folder, f"{name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        players_data = json.load(f)
    team = Team(name)
    team.players = [dict_to_player(p) for p in players_data]
    return team
