import tkinter as tk
from tkinter import ttk

from tabs.simulation_tab import SimulationTab
from tabs.standings_tab import StandingsTab
from tabs.schedule_tab import ScheduleTab
from tabs.roster_tab import RosterTab
from tabs.stats_tab import StatsTab

class TabManager:
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.tabs = {}
        self.playoff_tabs = {}
        self.playoff_tabs_visible = False

    def setup_tabs(self):
        """Setup all tabs"""
        main_frame = ttk.Frame(self.main_gui.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize regular season tabs
        self.tabs['simulation'] = SimulationTab(self.notebook, self.main_gui)
        self.tabs['standings'] = StandingsTab(self.notebook, self.main_gui)
        self.tabs['schedule'] = ScheduleTab(self.notebook, self.main_gui)
        self.tabs['roster'] = RosterTab(self.notebook, self.main_gui)
        self.tabs['stats'] = StatsTab(self.notebook, self.main_gui)

        # Store references for backward compatibility
        self.main_gui.simulation_tab = self.tabs['simulation']
        self.main_gui.standings_tab = self.tabs['standings']
        self.main_gui.schedule_tab = self.tabs['schedule']
        self.main_gui.roster_tab = self.tabs['roster']
        self.main_gui.stats_tab = self.tabs['stats']

    def show_playoff_tabs(self):
        """Show playoff-specific tabs when playoffs begin"""
        if self.playoff_tabs_visible:
            return

        # print("Adding playoff tabs...")

        try:
            from tabs.playoff_bracket_tab import PlayoffBracketTab
            from tabs.playoff_stats_tab import PlayoffStatsTab

            # Add playoff tabs
            self.playoff_tabs['bracket'] = PlayoffBracketTab(self.notebook, self.main_gui)
            self.playoff_tabs['playoff_stats'] = PlayoffStatsTab(self.notebook, self.main_gui)

            self.playoff_tabs_visible = True

            # Switch to playoff bracket tab
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text") == "Playoff Bracket":
                    self.notebook.select(i)
                    break

        except ImportError as e:
            print(f"Could not import playoff tabs: {e}")

    def hide_playoff_tabs(self):
        """Hide playoff tabs when season is reset"""
        if not self.playoff_tabs_visible:
            return

        # Remove playoff tabs from notebook
        tabs_to_remove = []
        for i in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(i, "text")
            if tab_text in ["Playoff Bracket", "Playoff Stats"]:
                tabs_to_remove.append(i)

        # Remove in reverse order to maintain indices
        for tab_index in reversed(tabs_to_remove):
            self.notebook.forget(tab_index)

        self.playoff_tabs.clear()
        self.playoff_tabs_visible = False

    def update_all_displays(self):
        """Update all tab displays"""
        for tab in self.tabs.values():
            if hasattr(tab, 'update_display'):
                tab.update_display()

        # FIXED: Update playoff tabs if visible
        if self.playoff_tabs_visible:
            for tab in self.playoff_tabs.values():
                if hasattr(tab, 'update_display'):
                    try:
                        tab.update_display()
                    except Exception as e:
                        print(f"Error updating playoff tab: {e}")
