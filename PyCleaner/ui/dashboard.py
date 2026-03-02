import customtkinter as ctk
import os
import threading
import time
from ui.design_system import SPACING, CARD, get_font, ICONS, format_size
from ui.graph import GraphWidget

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, worker, theme, update_callback=None, start_loop=True):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self.update_callback = update_callback
        self.running = True
        self._setup_ui()
        if start_loop: self.start_loop()

    def _setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="DASHBOARD", font=get_font('h1'), text_color=self.theme['accent']).pack(anchor="w")
        ctk.CTkLabel(title_box, text="System health and real-time performance.", font=get_font('body'), text_color=self.theme['dim']).pack(anchor="w")

        # PRIVILEGE INDICATOR / ELEVATION BUTTON
        self.priv_btn = ctk.CTkButton(header, text="🛡️ RUN AS ROOT", width=160, height=40,
                                     fg_color=self.theme['error'] if not self.worker.is_root else self.theme['success'],
                                     text_color="#FFFFFF", font=get_font('label'),
                                     command=self.request_elevation)
        self.priv_btn.pack(side="right", padx=10)
        
        if self.worker.is_root:
            self.priv_btn.configure(text="🛡️ ROOT ACCESS", state="disabled")

        # Grid for Stats
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)

        secondary_color = self.theme.get('accent2', self.theme['accent'])

        # CPU Card
        self.cpu_card = self._create_stat_card(self.grid_frame, "CPU USAGE", self.theme['accent'], 0, 0)
        self.cpu_graph = GraphWidget(self.cpu_card, self.theme['accent'])
        self.cpu_graph.pack(fill="both", expand=True, padx=15, pady=15)

        # RAM Card
        self.ram_card = self._create_stat_card(self.grid_frame, "MEMORY USAGE", secondary_color, 0, 1)
        self.ram_graph = GraphWidget(self.ram_card, secondary_color)
        self.ram_graph.pack(fill="both", expand=True, padx=15, pady=15)

        # Storage Card
        self.disk_card = self._create_stat_card(self.grid_frame, "STORAGE HEALTH", self.theme['success'], 1, 0, columnspan=2)
        self.disk_list = ctk.CTkFrame(self.disk_card, fg_color="transparent")
        self.disk_list.pack(fill="both", expand=True, padx=20, pady=10)

    def request_elevation(self):
        self.priv_btn.configure(text="RESTARTING...", state="disabled")
        self.update_idletasks()
        self.worker.elevate()

    def start_loop(self):
        def loop():
            while self.running:
                try:
                    stats = self.worker.get_sys_info()
                    self.after(0, lambda s=stats: self._update_ui(s))
                    time.sleep(1.5)
                except: break
        threading.Thread(target=loop, daemon=True).start()

    def _create_stat_card(self, parent, title, color, r, c, columnspan=1):
        card = ctk.CTkFrame(parent, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        card.grid(row=r, column=c, columnspan=columnspan, sticky="nsew", padx=10, pady=10)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 0))
        ctk.CTkLabel(header, text=title, font=get_font('label'), text_color=self.theme['dim']).pack(side="left")
        lbl = ctk.CTkLabel(header, text="0%", font=get_font('h2'), text_color=color)
        lbl.pack(side="right")
        card.value_lbl = lbl
        return card

    def _update_ui(self, stats):
        if not self.winfo_exists(): return
        self.cpu_card.value_lbl.configure(text=f"{int(stats['cpu_percent'])}%")
        self.cpu_graph.add_point(stats['cpu_percent']/100)
        self.ram_card.value_lbl.configure(text=f"{int(stats['ram_percent'])}%")
        self.ram_graph.add_point(stats['ram_percent']/100)
        if not hasattr(self, '_last_disk') or time.time() - self._last_disk > 30:
            self._update_disks()
            self._last_disk = time.time()

    def _update_disks(self):
        for w in self.disk_list.winfo_children(): w.destroy()
        drives = self.worker.get_drives()
        for d in drives:
            row = ctk.CTkFrame(self.disk_list, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"{d['mountpoint']} ({d['device']})", font=get_font('body')).pack(side="left")
            bar_box = ctk.CTkFrame(row, fg_color="transparent")
            bar_box.pack(side="right", fill="x", expand=True, padx=20)
            bar = ctk.CTkProgressBar(bar_box, height=10, progress_color=self.theme['accent'])
            bar.pack(side="left", fill="x", expand=True)
            bar.set(d['percent']/100)
            ctk.CTkLabel(row, text=f"{d['percent']}%", font=get_font('label'), width=50).pack(side="right")

    def destroy(self):
        self.running = False
        super().destroy()
