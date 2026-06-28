#!/usr/bin/env python3
"""Nebula Game Launcher — fullscreen desktop app for Xvfb.
Keyboard/controller navigable, touch-compatible, reads apps.json."""

import tkinter as tk
import json, os, subprocess, sys

APPS_FILE = os.path.expanduser("~/.config/sunshine/apps.json")
ROMS_DIR = os.path.expanduser("~/ROMs")

# Dark theme colors
BG = "#080812"
CARD_BG = "#0e0e1a"
TEXT = "#c0c0d0"
ACCENT = "#7c6af0"
SELECTED = "#141428"
HIGHLIGHT = "#9c8cff"
SUBTLE = "#404060"

class GameLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NEBULA")
        self.root.configure(bg=BG)
        self.root.attributes("-fullscreen", True)
        
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        
        # Fonts
        self.title_font = ("DejaVu Sans Mono", 24, "bold")
        self.card_font = ("DejaVu Sans Mono", 13)
        self.small_font = ("DejaVu Sans Mono", 9)
        
        # Key bindings
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Up>", lambda e: self.move(-1, 0))
        self.root.bind("<Down>", lambda e: self.move(1, 0))
        self.root.bind("<Left>", lambda e: self.move(0, -1))
        self.root.bind("<Right>", lambda e: self.move(0, 1))
        self.root.bind("<Return>", lambda e: self.launch_selected())
        self.root.bind("z", lambda e: self.launch_selected())
        self.root.bind("x", lambda e: self.root.destroy())
        self.root.bind("q", lambda e: self.launch_selected())  # L button
        self.root.bind("w", lambda e: self.scan_roms())         # R button
        
        # Header
        self.header = tk.Label(
            self.root, text="NEBULA  GAME  HUB", font=self.title_font,
            fg=ACCENT, bg=BG
        )
        self.header.pack(pady=(sh * 0.05, 10))
        
        self.subtitle = tk.Label(
            self.root, text="controller / keyboard / touch", font=self.small_font,
            fg=SUBTLE, bg=BG
        )
        self.subtitle.pack(pady=(0, 20))
        
        # Game grid frame
        self.grid_frame = tk.Frame(self.root, bg=BG)
        self.grid_frame.pack(expand=True, fill="both", padx=40, pady=10)
        
        # Status bar
        self.status = tk.Label(
            self.root, text="A/Z:launch  B/X:quit  L:launch  R:scan ROMs",
            font=self.small_font, fg=SUBTLE, bg=BG
        )
        self.status.pack(side="bottom", pady=15)
        
        self.cards = []
        self.selected = 0
        self.cols = 4
        self.load_games()
        
        self.root.mainloop()
    
    def load_games(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.cards = []
        
        try:
            with open(APPS_FILE) as f:
                data = json.load(f)
            games = data.get("apps", [])
        except:
            games = []
        
        for i, game in enumerate(games):
            name = game.get("name", "???")
            cmd = game.get("cmd", "")
            
            card = tk.Frame(
                self.grid_frame, bg=CARD_BG,
                highlightthickness=1, highlightbackground=SUBTLE,
                width=180, height=100
            )
            card.pack_propagate(False)
            
            # Game icon (first letter)
            icon = tk.Label(
                card, text=name[0].upper() if name else "?",
                font=("DejaVu Sans Mono", 28, "bold"),
                fg=ACCENT, bg=CARD_BG
            )
            icon.pack(pady=(10, 2))
            
            # Game name
            label = tk.Label(
                card, text=name, font=self.card_font,
                fg=TEXT, bg=CARD_BG, wraplength=170,
                justify="center"
            )
            label.pack(pady=(0, 2))
            
            # System tag if ROM
            if name.startswith("[") and "]" in name:
                tag_text = name[1:name.index("]")]
            else:
                tag_text = "native"
            
            tag = tk.Label(
                card, text=tag_text.upper(), font=self.small_font,
                fg=SUBTLE, bg=CARD_BG
            )
            tag.pack()
            
            card.bind("<Button-1>", lambda e, idx=i: self.select_and_launch(idx))
            icon.bind("<Button-1>", lambda e, idx=i: self.select_and_launch(idx))
            label.bind("<Button-1>", lambda e, idx=i: self.select_and_launch(idx))
            tag.bind("<Button-1>", lambda e, idx=i: self.select_and_launch(idx))
            
            # Layout in grid
            row, col = divmod(i, self.cols)
            card.grid(row=row, column=col, padx=8, pady=8)
            
            self.cards.append({
                "frame": card,
                "icon": icon,
                "label": label,
                "tag": tag,
                "name": name,
                "cmd": cmd,
            })
        
        if self.cards:
            self.highlight(0)
        
        self.status.config(
            text=f"{len(games)} games  |  A/Z:launch  B/X:quit  L:launch  R:scan ROMs"
        )
    
    def highlight(self, idx):
        if not self.cards:
            return
        idx = idx % len(self.cards)
        self.selected = idx
        
        for i, card in enumerate(self.cards):
            if i == idx:
                card["frame"].configure(bg=SELECTED, highlightbackground=HIGHLIGHT, highlightthickness=2)
                card["icon"].configure(bg=SELECTED)
                card["label"].configure(bg=SELECTED)
                card["tag"].configure(bg=SELECTED)
            else:
                card["frame"].configure(bg=CARD_BG, highlightbackground=SUBTLE, highlightthickness=1)
                card["icon"].configure(bg=CARD_BG)
                card["label"].configure(bg=CARD_BG)
                card["tag"].configure(bg=CARD_BG)
    
    def move(self, dy, dx):
        if not self.cards:
            return
        row = self.selected // self.cols
        col = self.selected % self.cols
        total_rows = (len(self.cards) - 1) // self.cols
        
        new_row = max(0, min(total_rows, row + dy))
        new_col = max(0, min(self.cols - 1, col + dx))
        new_idx = new_row * self.cols + new_col
        
        if new_idx >= len(self.cards):
            new_idx = len(self.cards) - 1
        
        self.highlight(new_idx)
    
    def select_and_launch(self, idx):
        self.highlight(idx)
        self.launch_selected()
    
    def launch_selected(self):
        if not self.cards or self.selected >= len(self.cards):
            return
        
        game = self.cards[self.selected]
        cmd = game["cmd"]
        name = game["name"]
        
        self.status.config(text=f"Launching: {name}...")
        self.root.update()
        
        if cmd:
            env = {**os.environ, "DISPLAY": ":99"}
            subprocess.Popen(cmd, shell=True, env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def scan_roms(self):
        self.status.config(text="Scanning ROMs...")
        self.root.update()
        scanner = os.path.expanduser("~/nebula/server/scan-roms.sh")
        if os.path.exists(scanner):
            subprocess.run(["bash", scanner], env={**os.environ, "DISPLAY": ":99"})
            self.load_games()
            self.status.config(text="ROMs scanned! Games updated.")

if __name__ == "__main__":
    # Set DISPLAY if not already set
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":99"
    GameLauncher()
