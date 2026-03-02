import customtkinter as ctk
import tkinter as tk
from ui.design_system import CARD

class GraphWidget(ctk.CTkFrame):
    def __init__(self, master, color, height=CARD['graph_height'], simplified=False, **kwargs):
        super().__init__(master, height=height, **kwargs)
        self.color = color
        self.simplified = simplified
        self.canvas = ctk.CTkCanvas(self, height=height, bg=self._apply_appearance_mode(self._fg_color), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.data_points = [0] * 60
        self.height = height
        
    def add_point(self, value):
        """Value between 0.0 and 1.0"""
        self.data_points.pop(0)
        self.data_points.append(value)
        self.draw()
        
    def update_color(self, color):
        self.color = color
        self.draw()

    def draw(self):
        # Optimizations for AMD A4: Skip drawing if not visible or too small
        if not self.winfo_ismapped(): return
        
        w = self.canvas.winfo_width()
        if w < 10: return

        self.canvas.delete("all")
        h = self.height
        step = w / (len(self.data_points) - 1)
        
        points = []
        for i, val in enumerate(self.data_points):
            x = i * step
            y = h - (val * h)
            points.append(x)
            points.append(y)
            
        if len(points) >= 4:
            # Simplified drawing: No smooth=True (splines are slow), no stipple fill (slow on X11)
            # Just a clean line
            self.canvas.create_line(points, fill=self.color, width=1.5, capstyle=tk.ROUND)
