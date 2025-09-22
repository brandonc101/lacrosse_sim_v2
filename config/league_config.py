class LeagueConfig:
    def __init__(self):
        self.teams_names = [
            "Buffalo Glacier", "Richmond Rebellion", "Louisville Stampede",
            "Minneapolis Chill", "Phoenix Dustrunners", "San Jose Quakebirds",
            "Toronto Ironhawks", "Montreal Sentries", "Calgary Nightwolves",
            "Spokane Tempest", "El Paso Vortex", "Atlanta Firewing",
            "Boston Riptide", "Charlotte Thunder", "Seattle Storm", "Denver Rapids"
        ]

        self.conferences = {
            "Eastern": {
                "North": ["Buffalo Glacier", "Toronto Ironhawks", "Montreal Sentries", "Boston Riptide"],
                "South": ["Richmond Rebellion", "Louisville Stampede", "Atlanta Firewing", "Charlotte Thunder"]
            },
            "Western": {
                "North": ["Minneapolis Chill", "Calgary Nightwolves", "Spokane Tempest", "Seattle Storm"],
                "South": ["San Jose Quakebirds", "Phoenix Dustrunners", "El Paso Vortex", "Denver Rapids"]
            }
        }

        self.divisions = {
            "Eastern North": self.conferences["Eastern"]["North"],
            "Eastern South": self.conferences["Eastern"]["South"],
            "Western North": self.conferences["Western"]["North"],
            "Western South": self.conferences["Western"]["South"]
        }

        # UPDATED for 14-week schedule
        self.regular_season_weeks = 14
        self.playoff_weeks = 3
        self.total_season_weeks = 17

    def get_team_conference(self, team_name):
        """Get the conference for a team"""
        for conference, divisions in self.conferences.items():
            for division, teams in divisions.items():
                if team_name in teams:
                    return conference
        return "Unknown"

    def get_team_division(self, team_name):
        """Get the division for a team"""
        for conference, divisions in self.conferences.items():
            for division, teams in divisions.items():
                if team_name in teams:
                    return division
        return "Unknown"

    def get_team_full_division(self, team_name):
        """Get the full division name"""
        for div_name, teams in self.divisions.items():
            if team_name in teams:
                return div_name
        return "Unknown"

    def get_conference_teams(self, conference):
        """Get all teams in a conference"""
        if conference in self.conferences:
            teams = []
            for division, team_list in self.conferences[conference].items():
                teams.extend(team_list)
            return teams
        return []

    def get_division_teams(self, conference, division):
        """Get teams in a specific division"""
        if conference in self.conferences and division in self.conferences[conference]:
            return self.conferences[conference][division]
        return []
