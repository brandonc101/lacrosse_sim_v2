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

    def setup_tabs(self):
        """Setup all tabs"""
        main_frame = ttk.Frame(self.main_gui.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Initialize all tabs
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

    def update_all_displays(self):
        """Update all tab displays"""
        for tab in self.tabs.values():
            if hasattr(tab, 'update_display'):
                tab.update_display()
