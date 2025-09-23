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

        self.season_progress = ttk.Progressbar(week_info_frame, length=400, mode='determinate', maximum=18)
        self.season_progress.pack(pady=5)

        self.progress_label = ttk.Label(week_info_frame, text="Regular Season: 0/14 weeks", font=("Arial", 10))
        self.progress_label.pack(pady=2)

        # Control buttons (REMOVED reset button)
        button_frame = ttk.Frame(sim_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.sim_week_btn = ttk.Button(button_frame, text="Simulate Next Week",
                                      command=self.simulate_next_week, style="Accent.TButton")
        self.sim_week_btn.pack(side=tk.LEFT, padx=5)

        self.sim_season_btn = ttk.Button(button_frame, text="Simulate Entire Season",
                                       command=self.simulate_entire_season)
        self.sim_season_btn.pack(side=tk.LEFT, padx=5)

        # Recent games display
        recent_frame = ttk.LabelFrame(sim_frame, text="Recent Games", padding=10)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.recent_games_text = scrolledtext.ScrolledText(recent_frame, height=15, width=80)
        self.recent_games_text.pack(fill=tk.BOTH, expand=True)

    def simulate_next_week(self):
        """Simulate the next week of games with proper error handling"""
        try:
            # Check if season is complete
            if hasattr(self.main_gui, 'season_complete') and self.main_gui.season_complete:
                messagebox.showinfo("Season Complete", "The season has already been completed!")
                return

            # Simulate the week
            results_text = self.main_gui.game_simulator.simulate_next_week()

            if results_text:
                self.recent_games_text.delete(1.0, tk.END)
                self.recent_games_text.insert(tk.END, results_text)
            else:
                self.recent_games_text.delete(1.0, tk.END)
                self.recent_games_text.insert(tk.END, "No games or events this week.")

            # Check if playoff preparation week just happened
            if (hasattr(self.main_gui, 'current_week') and
                self.main_gui.current_week == 15 and
                hasattr(self.main_gui, 'tab_manager')):
                self.main_gui.tab_manager.show_playoff_tabs()

            # Update all displays
            self.update_display()
            if hasattr(self.main_gui, 'update_all_displays'):
                self.main_gui.update_all_displays()

        except Exception as e:
            print(f"Error in simulate_next_week: {e}")
            messagebox.showerror("Simulation Error", f"Error simulating week: {str(e)}")

    def simulate_entire_season(self):
        """Simulate the entire remaining season with error handling"""
        try:
            if hasattr(self.main_gui, 'season_complete') and self.main_gui.season_complete:
                messagebox.showinfo("Season Complete", "The season has already been completed!")
                return

            result = messagebox.askyesno("Confirm", "Are you sure you want to simulate the entire remaining season?")
            if result:
                week_count = self.main_gui.game_simulator.simulate_entire_season()
                messagebox.showinfo("Season Complete", f"Season simulation completed in {week_count} weeks!")

                # Update displays
                self.update_display()
                if hasattr(self.main_gui, 'update_all_displays'):
                    self.main_gui.update_all_displays()

        except Exception as e:
            print(f"Error in simulate_entire_season: {e}")
            messagebox.showerror("Simulation Error", f"Error during season simulation: {str(e)}")

    def _update_progress_label(self):
        """Update the progress label with detailed season info"""
        try:
            if not hasattr(self.main_gui, 'current_week'):
                self.progress_label.config(text="Regular Season: 0/14 weeks")
                return

            current_week = self.main_gui.current_week

            if current_week <= 14:
                # Regular season
                self.progress_label.config(text=f"Regular Season: {current_week}/14 weeks")
            elif current_week == 15:
                # Playoff preparation
                self.progress_label.config(text="Playoff Preparation Week - Brackets Set")
            elif current_week <= 18:
                # Playoffs
                playoff_week = current_week - 15
                self.progress_label.config(text=f"Playoffs: {playoff_week}/3 weeks")
            else:
                # Offseason
                self.progress_label.config(text="Season Complete - Offseason")

        except Exception as e:
            print(f"Error updating progress label: {e}")
            self.progress_label.config(text="Progress unavailable")

    def update_display(self):
        """Update the simulation tab display with error handling"""
        try:
            # Update week label
            if hasattr(self.main_gui, 'current_week'):
                self.week_label.config(text=f"Current Week: {self.main_gui.current_week}")
                self.season_progress['value'] = self.main_gui.current_week
            else:
                self.week_label.config(text="Current Week: 0")
                self.season_progress['value'] = 0

            # Update progress label
            self._update_progress_label()

        except Exception as e:
            print(f"Error updating simulation display: {e}")
            self.week_label.config(text="Current Week: Error")
            self.progress_label.config(text="Error updating display")
