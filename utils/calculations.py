import math

def calculate_overall_rating(player, position):
    """Calculate position-weighted overall rating"""
    shooting = getattr(player, 'shooting', 70)
    passing = getattr(player, 'passing', 70)
    defense = getattr(player, 'defense', 70)
    stamina = getattr(player, 'stamina', 70)

    # Position-specific weightings
    if position == "Attack":
        weights = {"shooting": 0.45, "passing": 0.25, "stamina": 0.20, "defense": 0.10}
    elif position == "Midfield":
        weights = {"passing": 0.30, "stamina": 0.30, "shooting": 0.25, "defense": 0.15}
    elif position == "Defense":
        weights = {"defense": 0.50, "stamina": 0.25, "passing": 0.15, "shooting": 0.10}
    elif position == "Goalie":
        weights = {"defense": 0.60, "stamina": 0.25, "passing": 0.10, "shooting": 0.05}
    else:
        weights = {"shooting": 0.25, "passing": 0.25, "defense": 0.25, "stamina": 0.25}

    overall = (
        shooting * weights["shooting"] +
        passing * weights["passing"] +
        defense * weights["defense"] +
        stamina * weights["stamina"]
    )

    return math.floor(overall)
