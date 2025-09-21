import random
import json
from typing import List, Dict, Optional
from enum import Enum

class Position(Enum):
    ATTACK = "Attack"
    MIDFIELDER = "Midfield"  # Changed to match your existing code
    DEFENSEMAN = "Defense"   # Changed to match your existing code
    GOALIE = "Goalie"

class NameGenerator:
    def __init__(self):
        # First names for lacrosse players
        self.first_names = [
            # Common American first names popular in lacrosse
            "Connor", "Ryan", "Tyler", "Jake", "Matt", "Mike", "Chris", "Dan", "Kevin", "Brian",
            "Sean", "Patrick", "Michael", "Andrew", "David", "John", "James", "Robert", "William",
            "Thomas", "Alex", "Nick", "Ben", "Sam", "Josh", "Luke", "Noah", "Jack", "Owen",
            "Mason", "Ethan", "Liam", "Logan", "Lucas", "Hunter", "Cole", "Blake", "Drew", "Trey",
            "Chase", "Austin", "Brendan", "Garrett", "Trevor", "Kyle", "Jordan", "Derek", "Colin",
            "Brady", "Zach", "Cody", "Grant", "Carson", "Bryce", "Ian", "Carter", "Shane", "Reid",
            "Caleb", "Parker", "Devon", "Evan", "Nolan", "Aidan", "Max", "Cooper", "Jace",
            "Wyatt", "Brayden", "Colton", "Landon", "Gavin", "Tristan", "Tanner", "Ryder",
            "Camden", "Griffin", "Brody", "Kaden", "Easton", "Paxton", "Reese", "Finn", "Miles",
            "Sawyer", "Declan", "Hudson", "Jaxon", "Bentley", "Grayson", "Lincoln", "Harrison"
        ]

        # Last names - mix of common American surnames and some with lacrosse heritage
        self.last_names = [
            # Common American surnames
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
            "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor",
            "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez",
            "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright",
            "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker",
            "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts", "Gomez", "Phillips",
            "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart",

            # Names with lacrosse/sports heritage
            "McBride", "O'Connor", "Sullivan", "Murphy", "Kelly", "Ryan", "Walsh", "O'Brien",
            "McCarthy", "Fitzgerald", "Kennedy", "Brennan", "Quinn", "Flanagan", "Mahoney",
            "Donovan", "Gallagher", "McDonnell", "Flynn", "Brady", "Casey", "Daly", "Kane",
            "Lynch", "Burke", "Duffy", "Connolly", "Shannon", "O'Neill", "Malone", "Byrne",
            "Rourke", "McGrath", "O'Sullivan", "Shea", "Callahan", "Hogan", "MacLeod", "Fraser",
            "Cameron", "Murray", "Ross", "Grant", "Reid", "Bell", "Graham", "Duncan", "McKenzie",
            "Hamilton", "Henderson", "Patterson", "Ferguson", "Bennett", "Morgan", "Powell"
        ]

    def generate_name(self) -> tuple:
        """Generate a random first and last name combination"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        return first_name, last_name

    def generate_full_name(self) -> str:
        """Generate a full name as a string"""
        first_name, last_name = self.generate_name()
        return f"{first_name} {last_name}"

class TeamRosterManager:
    def __init__(self):
        self.name_generator = NameGenerator()
        self.team_rosters = {}
        self.load_or_create_rosters()

    def create_default_rosters(self, team_names: List[str]) -> Dict[str, List[str]]:
        """Create default rosters for all teams with realistic names"""
        rosters = {}

        for team_name in team_names:
            roster = []
            # Create 10 players per team (matching your current logic)
            # 3 Attack, 3 Midfield, 3 Defense, 1 Goalie
            positions = ['Attack', 'Attack', 'Attack', 'Midfield', 'Midfield', 'Midfield',
                        'Defense', 'Defense', 'Defense', 'Goalie']

            used_names = set()
            for position in positions:
                # Generate unique names for each player
                while True:
                    name = self.name_generator.generate_full_name()
                    if name not in used_names:
                        used_names.add(name)
                        roster.append({
                            'name': name,
                            'position': position
                        })
                        break

            rosters[team_name] = roster

        return rosters

    def get_player_name(self, team_name: str, position: str, player_index: int) -> str:
        """Get a specific player name for a team and position"""
        if team_name not in self.team_rosters:
            return f"{team_name} Player{player_index+1}"  # Fallback to original naming

        roster = self.team_rosters[team_name]

        # Find players with matching position
        players_in_position = [p for p in roster if p['position'] == position]

        if player_index < len(players_in_position):
            return players_in_position[player_index]['name']

        # Fallback if not enough players in that position
        return f"{team_name} Player{player_index+1}"

    def get_team_roster(self, team_name: str) -> List[Dict]:
        """Get the full roster for a team"""
        return self.team_rosters.get(team_name, [])

    def generate_draft_players(self, count: int = 50) -> List[Dict]:
        """Generate random players for draft"""
        draft_players = []

        # Distribution for draft players
        position_weights = {
            'Attack': 0.25,
            'Midfield': 0.35,
            'Defense': 0.25,
            'Goalie': 0.15
        }

        used_names = set()
        # Get all existing names to avoid duplicates
        for roster in self.team_rosters.values():
            for player in roster:
                used_names.add(player['name'])

        for _ in range(count):
            # Choose position based on weights
            position = random.choices(
                list(position_weights.keys()),
                weights=list(position_weights.values())
            )[0]

            # Generate unique name
            while True:
                name = self.name_generator.generate_full_name()
                if name not in used_names:
                    used_names.add(name)
                    break

            # Generate realistic stats
            draft_players.append({
                'name': name,
                'position': position,
                'shooting': random.randint(45, 95),
                'passing': random.randint(45, 95),
                'defense': random.randint(45, 95),
                'stamina': random.randint(45, 95)
            })

        return draft_players

    def save_rosters_to_file(self, filename: str = "team_rosters.json") -> None:
        """Save all team rosters to a JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.team_rosters, f, indent=2)
        except Exception as e:
            print(f"Error saving rosters: {e}")

    def load_rosters_from_file(self, filename: str = "team_rosters.json") -> bool:
        """Load team rosters from a JSON file"""
        try:
            with open(filename, 'r') as f:
                self.team_rosters = json.load(f)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error loading rosters: {e}")
            return False

    def load_or_create_rosters(self, team_names: List[str] = None):
        """Load existing rosters or create new ones"""
        if not self.load_rosters_from_file():
            # If no saved rosters exist, create default ones when team names are available
            if team_names:
                self.team_rosters = self.create_default_rosters(team_names)
                self.save_rosters_to_file()

    def initialize_for_teams(self, team_names: List[str]):
        """Initialize rosters for a specific list of teams"""
        # Check if we need to create rosters for new teams
        needs_update = False

        for team_name in team_names:
            if team_name not in self.team_rosters:
                needs_update = True
                # Create roster for this team
                roster = []
                positions = ['Attack', 'Attack', 'Attack', 'Midfield', 'Midfield', 'Midfield',
                            'Defense', 'Defense', 'Defense', 'Goalie']

                used_names = set()
                # Get all existing names to avoid duplicates
                for existing_roster in self.team_rosters.values():
                    for player in existing_roster:
                        used_names.add(player['name'])

                for position in positions:
                    while True:
                        name = self.name_generator.generate_full_name()
                        if name not in used_names:
                            used_names.add(name)
                            roster.append({
                                'name': name,
                                'position': position
                            })
                            break

                self.team_rosters[team_name] = roster

        if needs_update:
            self.save_rosters_to_file()

    def get_roster_summary(self, team_name: str) -> str:
        """Get a formatted string summary of a team's roster"""
        if team_name not in self.team_rosters:
            return f"No roster found for {team_name}"

        roster = self.team_rosters[team_name]
        output = [f"\n{team_name} Roster:"]
        output.append("=" * (len(team_name) + 8))

        # Group by position
        positions = ['Attack', 'Midfield', 'Defense', 'Goalie']
        for position in positions:
            players = [p for p in roster if p['position'] == position]
            if players:
                output.append(f"\n{position}s ({len(players)}):")
                for player in sorted(players, key=lambda p: p['name']):
                    output.append(f"  {player['name']}")

        output.append(f"\nTotal Players: {len(roster)}")
        return "\n".join(output)

# Global instance for easy access
roster_manager = TeamRosterManager()

def get_player_name_for_team(team_name: str, position: str, player_index: int) -> str:
    """
    Convenience function to get a player name.
    This is the main function you'll use in your existing code.
    """
    return roster_manager.get_player_name(team_name, position, player_index)

def initialize_rosters_for_teams(team_names: List[str]):
    """
    Initialize rosters for your teams. Call this once in your GUI initialization.
    """
    roster_manager.initialize_for_teams(team_names)

def get_draft_players(count: int = 50) -> List[Dict]:
    """
    Generate draft players for your draft functionality.
    """
    return roster_manager.generate_draft_players(count)

def get_team_roster_display(team_name: str) -> str:
    """
    Get a formatted display of a team's roster.
    """
    return roster_manager.get_roster_summary(team_name)

# Example usage and testing
if __name__ == "__main__":
    # Test with your team names
    team_names = [
        "Buffalo Glacier", "Richmond Rebellion", "Louisville Stampede",
        "Minneapolis Chill", "Phoenix Dustrunners", "San Jose Quakebirds",
        "Toronto Ironhawks", "Montreal Sentries", "Calgary Nightwolves",
        "Spokane Tempest", "El Paso Vortex", "Atlanta Firewing"
    ]

    # Initialize rosters
    initialize_rosters_for_teams(team_names)

    # Test getting player names
    print("=== SAMPLE PLAYER NAMES ===")
    for team in team_names[:3]:  # Show first 3 teams
        print(f"\n{team}:")
        positions = ['Attack', 'Midfield', 'Defense', 'Goalie']
        for pos in positions:
            name = get_player_name_for_team(team, pos, 0)  # Get first player in each position
            print(f"  {pos}: {name}")

    # Test draft players
    print("\n=== SAMPLE DRAFT PLAYERS ===")
    draft_players = get_draft_players(10)
    for i, player in enumerate(draft_players[:5], 1):
        print(f"{i}. {player['name']} ({player['position']}) - Shooting: {player['shooting']}")

    print(f"\nRosters saved to team_rosters.json")
