import tkinter as tk
from tkinter import messagebox, filedialog

class MenuManager:
    def __init__(self, main_gui):
        self.main_gui = main_gui

    def setup_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.main_gui.root)
        self.main_gui.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New Season", command=self.new_season)
        file_menu.add_separator()
        file_menu.add_command(label="Save League", command=self.save_league)
        file_menu.add_command(label="Load League", command=self.load_league)
        file_menu.add_separator()
        file_menu.add_command(label="Quick Save", command=self.save_game)
        file_menu.add_command(label="Quick Load", command=self.load_game)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.main_gui.root.quit)

    def new_season(self):
        """Start a new season"""
        self.main_gui.game_simulator.reset_season()
        messagebox.showinfo("New Season", "New season started!")

    def save_league(self):
        """Save using DataManager"""
        if hasattr(self.main_gui, 'data_manager'):
            return self.main_gui.data_manager.save_league_data()
        else:
            messagebox.showerror("Error", "Data manager not initialized")

    def load_league(self):
        """Load using DataManager"""
        if hasattr(self.main_gui, 'data_manager'):
            return self.main_gui.data_manager.load_league_data()
        else:
            messagebox.showerror("Error", "Data manager not initialized")

    def save_game(self):
        """Quick save method"""
        try:
            import json
            save_data = self.main_gui.game_simulator.get_save_data()
            with open("lacrosse_save.json", "w") as f:
                json.dump(save_data, f, indent=2, default=str)
            messagebox.showinfo("Quick Save", "Game saved successfully!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving game: {str(e)}")

    def load_game(self):
        """Quick load method"""
        try:
            import json, os
            if os.path.exists("lacrosse_save.json"):
                with open("lacrosse_save.json", "r") as f:
                    save_data = json.load(f)
                self.main_gui.game_simulator.load_save_data(save_data)
                self.main_gui.update_all_displays()
                messagebox.showinfo("Quick Load", "Game loaded successfully!")
            else:
                messagebox.showwarning("Load Game", "No saved game found!")
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading game: {str(e)}")
