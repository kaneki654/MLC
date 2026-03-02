import customtkinter as ctk
import os
import time
import threading
from ui.design_system import SPACING, CARD, get_font

class Explorer(ctk.CTkFrame):
    def __init__(self, master, theme):
        super().__init__(master, fg_color="transparent")
        self.theme = theme
        self.current_path = os.path.expanduser("~")
        
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        # Toolbar
        tool_bar = ctk.CTkFrame(self, fg_color=self.theme['card'], height=45, corner_radius=CARD['corner_radius_sm'])
        tool_bar.pack(fill="x", pady=(0, SPACING['sm']))
        tool_bar.pack_propagate(False)

        ctk.CTkButton(tool_bar, text="UP", width=60, height=30, fg_color=self.theme['surface'], 
                     command=self.go_up).pack(side="left", padx=5)
        
        self.path_entry = ctk.CTkEntry(tool_bar, fg_color=self.theme['surface'], border_width=0, height=30)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.path_entry.bind("<Return>", lambda e: self._load_path(self.path_entry.get()))

        # Split List and Preview
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.pack(fill="both", expand=True)

        self.list_frame = ctk.CTkScrollableFrame(split, fg_color=self.theme['card'], corner_radius=CARD['corner_radius'])
        self.list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.preview_frame = ctk.CTkFrame(split, fg_color=self.theme['card'], width=250, corner_radius=CARD['corner_radius'])
        self.preview_frame.pack(side="right", fill="both")
        self.preview_frame.pack_propagate(False)

        self.prev_text = ctk.CTkTextbox(self.preview_frame, fg_color=self.theme['surface'], font=get_font('mono'))
        self.prev_text.pack(fill="both", expand=True, padx=5, pady=5)

    def refresh(self): self._load_path(self.current_path)

    def _load_path(self, path):
        if not os.path.isdir(path): return
        self.current_path = path
        self.path_entry.delete(0, 'end')
        self.path_entry.insert(0, path)
        
        for w in self.list_frame.winfo_children(): w.destroy()
        
        try:
            items = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for item in items:
                ctk.CTkButton(self.list_frame, text=f"[{'D' if item.is_dir() else 'F'}] {item.name}", 
                             fg_color="transparent", text_color=self.theme['text'], anchor="w",
                             command=lambda i=item: self._on_click(i)).pack(fill="x")
        except: pass

    def _on_click(self, item):
        if item.is_dir(): self._load_path(item.path)
        else:
            self.prev_text.delete("0.0", "end")
            try:
                with open(item.path, 'r', errors='ignore') as f:
                    self.prev_text.insert("0.0", f.read(1000))
            except: self.prev_text.insert("0.0", "Cannot preview.")

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path: self._load_path(parent)
