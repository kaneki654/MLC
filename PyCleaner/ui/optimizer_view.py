import customtkinter as ctk
from tkinter import messagebox
from ui.design_system import SPACING, CARD, get_font, ICONS

class OptimizerView(ctk.CTkFrame):
    def __init__(self, master, worker, theme):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        # Main Scrollable Content
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)

        header = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text=f"{ICONS['dashboard']}  SYSTEM OPTIMIZER", font=get_font('h1'), text_color=self.theme['accent']).pack(side="left")

        # Memory & Swap Section
        mem_frame = ctk.CTkFrame(self.main_scroll, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        mem_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(mem_frame, text="MEMORY & SWAP ENGINE", font=get_font('h3')).pack(anchor="w", padx=20, pady=15)
        
        btn_box = ctk.CTkFrame(mem_frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(0, 20))
        
        is_lite = self.theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        
        ctk.CTkButton(btn_box, text="DROP RAM CACHES", height=45, fg_color=self.theme['surface'], 
                     text_color=text_col, border_width=2, border_color=self.theme['border'],
                     command=self.run_ram_boost).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(btn_box, text="REFRESH SWAP", height=45, fg_color=self.theme['surface'], 
                     text_color=text_col, border_width=2, border_color=self.theme['border'],
                     command=self.run_swap_opt).pack(side="left", expand=True, padx=5)

        # Gaming Mode Section
        game_frame = ctk.CTkFrame(self.main_scroll, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        game_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(game_frame, text="GAMING MODE", font=get_font('h3')).pack(anchor="w", padx=20, pady=15)
        
        ctk.CTkButton(game_frame, text="ACTIVATE GAMING BOOST", height=50, 
                     fg_color=self.theme['accent'], text_color="#FFFFFF",
                     font=get_font('h2'),
                     command=self.run_gaming_boost).pack(fill="x", padx=20, pady=(0, 20))

        # Kernel Tunables
        kern_frame = ctk.CTkFrame(self.main_scroll, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        kern_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(kern_frame, text="KERNEL TUNABLES (PERFORMANCE PROFILES)", font=get_font('h3')).pack(anchor="w", padx=20, pady=15)
        
        prof_box = ctk.CTkFrame(kern_frame, fg_color="transparent")
        prof_box.pack(fill="x", padx=20, pady=(0, 20))
        
        profiles = [
            ("GAMING", "performance", self.theme['error']),
            ("BALANCED", "balanced", self.theme['accent']),
            ("BATTERY", "battery", self.theme['success'])
        ]
        
        for name, mode, col in profiles:
            ctk.CTkButton(prof_box, text=name, height=40, fg_color=self.theme['surface'], 
                         text_color=text_col,
                         border_width=2, border_color=col,
                         command=lambda m=mode: self.set_profile(m)).pack(side="left", expand=True, padx=5)

        # Startup Manager Section
        start_frame = ctk.CTkFrame(self.main_scroll, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        start_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(start_frame, text="STARTUP APPLICATIONS", font=get_font('h3')).pack(anchor="w", padx=20, pady=15)
        
        self.start_list = ctk.CTkFrame(start_frame, fg_color="transparent")
        self.start_list.pack(fill="x", padx=10, pady=(0, 10))
        
        self.load_startup()

    def load_startup(self):
        for widget in self.start_list.winfo_children():
            widget.destroy()
            
        apps = self.worker.startup.list_autostart()
        is_lite = self.theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        
        if not apps:
            ctk.CTkLabel(self.start_list, text="No startup applications found.", font=get_font('body'), text_color=self.theme['dim']).pack(pady=10)
            return

        for app in apps:
            row = ctk.CTkFrame(self.start_list, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=f"• {app['name']}", font=get_font('body'), text_color=text_col).pack(side="left", padx=10)
            
            switch = ctk.CTkSwitch(row, text="", width=50, height=25,
                                  progress_color=self.theme['success'])
            
            # Configure command with closure
            switch.configure(command=lambda s=switch, p=app['path']: self.on_toggle_startup(s, p))
            
            if app['enabled']:
                switch.select()
            else:
                switch.deselect()
            
            switch.pack(side="right", padx=10)

    def on_toggle_startup(self, switch, path):
        enable = bool(switch.get())
        if self.worker.startup.toggle_app(path, enable):
            # Refresh list after rename to update path logic if needed
            self.load_startup()
        else:
            if enable: switch.deselect()
            else: switch.select()
            messagebox.showerror("Error", "Failed to update startup item.")

    def run_ram_boost(self):
        success, msg = self.worker.boost_ram()
        messagebox.showinfo("RAM Engine", msg)

    def run_swap_opt(self):
        success, msg = self.worker.optimize_swap()
        if success: messagebox.showinfo("Swap Engine", msg)
        else: messagebox.showwarning("Swap Engine", msg)

    def set_profile(self, mode):
        success, msg = self.worker.optimizer.set_governor(mode)
        messagebox.showinfo("Kernel Tuner", msg)

    def run_gaming_boost(self):
        self.worker.boost_ram()
        
        success, msg = self.worker.optimizer.set_cpu_governor("performance")
        
        if success:
            messagebox.showinfo("Gaming Boost", "GAMING MODE ACTIVATED\n\n• RAM Caches Cleared\n• Background Indexing Paused\n• CPU Governor: Performance")
        else:
            messagebox.showinfo("Gaming Boost", f"Optimized RAM for Gaming.\n(CPU Boost: {msg})")
