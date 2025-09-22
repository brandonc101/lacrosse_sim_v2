import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class SimulationTab:
    def __init__(self, notebook, main_gui):
        self.main_gui = main_gui
        self.setup_tab(notebook)

    def setup_tab(self, notebook):
        sim_frame = ttk.Frame(notebook)
        notebook.add(sim_frame, text="Simulation Control")

        # Week information
        week_info_frame = ttk.LabelFrame(sim_frame, text="Season Progress", padding=10)
        week_info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.week_label = ttk.Label(week_info_frame, text="Current Week: 0", font=("Arial", 12, "bold"))
        self.week_label.pack(pady=5)

        self.season_progress = ttk.Progressbar(week_info_frame, length=400, mode='determinate', maximum=15)
        self.season_progress.pack(pady=5)

        self.progress_label = ttk.Label(week_info_frame, text="Regular Season: 0/12 weeks", font=("Arial", 10))
        self.progress_label.pack(pady=2)

        # Control buttons
        button_frame = ttk.Frame(sim_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.sim_week_btn = ttk.Button(button_frame, text="Simulate Next Week",
                                      command=self.simulate_next_week, style="Accent.TButton")
        self.sim_week_btn.pack(side=tk.LEFT, padx=5)

        self.sim_season_btn = ttk.Button(button_frame, text="Simulate Entire Season",
                                       command=self.simulate_entire_season)
        self.sim_season_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(button_frame, text="Reset Season", command=self.reset_season)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Recent games display
        recent_frame = ttk.LabelFrame(sim_frame, text="Recent Games", padding=10)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.recent_games_text = scrolledtext.ScrolledText(recent_frame, height=15, width=80)
        self.recent_games_text.pack(fill=tk.BOTH, expand=True)

    def simulate_next_week(self):
        """Simulate the next week of games"""
        results_text = self.main_gui.game_simulator.simulate_next_week()
        if results_text:
            self.recent_games_text.delete(1.0, tk.END)
            self.recent_games_text.insert(tk.END, results_text)

        # Update displays
        self.week_label.config(text=f"Current Week: {self.main_gui.current_week}")
        self.season_progress['value'] = self.main_gui.current_week
        self._update_progress_label()
        self.main_gui.update_all_displays()

    def simulate_entire_season(self):
        """Simulate the entire remaining season"""
        if self.main_gui.season_complete:
            messagebox.showinfo("Season Complete", "The season has already been completed!")
            return

        result = messagebox.askyesno("Confirm", "Are you sure you want to simulate the entire remaining season?")
        if result:
            try:
                week_count = self.main_gui.game_simulator.simulate_entire_season()
                messagebox.showinfo("Season Complete", f"Season simulation completed in {week_count} weeks!")
                self.main_gui.update_all_displays()
                self._update_progress_label()
            except Exception as e:
                messagebox.showerror("Simulation Error", f"Error during simulation: {str(e)}")

    def reset_season(self):
        """Reset the season to the beginning"""
        result = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the season? All progress will be lost.")
        if result:
            self.main_gui.game_simulator.reset_season()
            self.week_label.config(text="Current Week: 0")
            self.season_progress['value'] = 0
            self.progress_label.config(text="Regular Season: 0/12 weeks")
            self.recent_games_text.delete(1.0, tk.END)
            self.main_gui.update_all_displays()

    def _update_progress_label(self):
        """Update the progress label with detailed season info"""
        current_week = self.main_gui.current_week

        if current_week <= 12:
            # Regular season
            self.progress_label.config(text=f"Regular Season: {current_week}/12 weeks")
        elif current_week <= 15:
            # Playoffs
            playoff_week = current_week - 12
            self.progress_label.config(text=f"Playoffs: {playoff_week}/3 weeks (Regular season complete)")
        else:
            # Offseason
            self.progress_label.config(text="Season Complete - Offseason")

    def update_display(self):
        """Update the simulation tab display"""
        self.week_label.config(text=f"Current Week: {self.main_gui.current_week}")
        self.season_progress['value'] = self.main_gui.current_week
        self._update_progress_label()
