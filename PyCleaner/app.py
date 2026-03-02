import customtkinter as ctk
import os
import threading
import time
from tkinter import messagebox, filedialog
from backend import ScannerWorker
from ui.themes import ThemeManager
from ui.dashboard import Dashboard
from ui.explorer import Explorer
from ui.scan_view import ScanView
from ui.toolbox_view import ToolboxView
from ui.dev_view import DevHubView
from ui.process_view import ProcessView
from ui.optimizer_view import OptimizerView
from ui.health_view import HealthView
from ui.info_view import InfoView
from ui.sound import play_sound
from ui.design_system import SPACING, get_font, ICONS, SIDEBAR, CARD


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.worker = ScannerWorker(self.get_auth)
        
        # VISUAL ROOT INDICATOR
        title_str = "MLCleaner v0.3.1.2"
        if self.worker.is_root:
            title_str += " (ROOT ACCESS)"
            
        self.title(title_str)
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        self.tm = ThemeManager()
        self.theme = self.tm.get()
        self.current_frame = None
        
        self.configure(fg_color=self.theme['bg'])
        self._setup_layout()
        self.show_dashboard()

    def _setup_layout(self):
        # Sidebar Frame - Fixed Rail
        self.sidebar = ctk.CTkFrame(self, width=SIDEBAR['width'], fg_color=self.theme['card'], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Content Frame
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="right", fill="both", expand=True)

        # Logo at top
        ctk.CTkLabel(self.sidebar, text="ML", font=get_font('h1'), text_color=self.theme['accent']).pack(pady=(20, 10))
        ctk.CTkFrame(self.sidebar, height=2, width=40, fg_color=self.theme['border']).pack()

        # Nav Buttons
        self.nav_items = [
            (ICONS['dashboard'], self.show_dashboard),
            (ICONS['scan'], self.show_scan),
            (ICONS['activity'], self.show_process_sentinel),
            ('🚀', self.show_optimizer),
            ('🏥', self.show_health),
            ('ℹ️', self.show_info),
            (ICONS['files'], self.show_explorer),
            (ICONS['tools'], self.show_tools),
            (ICONS['dev'], self.show_dev),
            (ICONS['settings'], self.show_settings)
        ]
        
        self.nav_btns = []
        for icon, cmd in self.nav_items:
            # White text for high visibility in dark mode
            is_lite = self.theme.get('bg') == "#F2F2F2"
            text_col = "#000000" if is_lite else "#FFFFFF"
            btn = ctk.CTkButton(self.sidebar, text=icon, width=SIDEBAR['width']-20, height=50,
                               anchor="center", fg_color="transparent", text_color=text_col,
                               hover_color=self.theme['surface'], font=get_font('h2'),
                               corner_radius=CARD['corner_radius_sm'],
                               border_width=2, border_color=self.theme['border'],
                               command=cmd)
            btn.pack(pady=5, padx=10)
            self.nav_btns.append(btn)

        # Bottom Theme Switcher
        is_lite = self.theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        self.theme_btn = ctk.CTkButton(self.sidebar, text="🌓", width=40, height=40,
                                      fg_color="transparent", text_color=text_col,
                                      command=self.next_theme)
        self.theme_btn.pack(side="bottom", pady=25)

    def next_theme(self):
        names = list(self.tm.THEMES.keys())
        idx = (names.index(self.tm.current) + 1) % len(names)
        self.change_theme(names[idx])

    def change_theme(self, name):
        self.theme = self.tm.set_theme(name)
        ctk.set_appearance_mode("Light" if name == "Lite" else "Dark")
        for widget in self.winfo_children(): widget.destroy()
        self.configure(fg_color=self.theme['bg'])
        self._setup_layout()
        self.show_dashboard()

    def _switch(self, frame_class, *args):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = frame_class(self.content, *args)
        self.current_frame.pack(fill="both", expand=True, padx=SPACING['page'], pady=SPACING['page'])

    def get_auth(self):
        """Callback to open password dialog."""
        from ui.components import PasswordDialog
        dialog = PasswordDialog(self, self.theme)
        return dialog.password

    def show_dashboard(self): 
        self._switch(Dashboard, self.worker, self.theme, None, True)
        if hasattr(self.current_frame, 'start_loop'):
            self.current_frame.start_loop()
    def show_scan(self): self._switch(ScanView, self.worker, self.theme, True)
    def show_process_sentinel(self):
        self._switch(ProcessView, self.worker, self.theme)
        if hasattr(self.current_frame, 'start_loop'):
            self.current_frame.start_loop()
    
    def show_optimizer(self):
        self._switch(OptimizerView, self.worker, self.theme)

    def show_health(self):
        self._switch(HealthView, self.worker, self.theme)

    def show_info(self):
        self._switch(InfoView, self.worker, self.theme)

    def show_explorer(self): self._switch(Explorer, self.theme)
    def show_tools(self): self._switch(ToolboxView, self.worker, self.theme)
    def show_dev(self): self._switch(DevHubView, self.worker, self.theme)
    def show_settings(self):
        self._switch(ctk.CTkFrame)
        ctk.CTkLabel(self.current_frame, text="SETTINGS", font=get_font('h1'), text_color=self.theme['accent']).pack(pady=20)
        ctk.CTkLabel(self.current_frame, text="MLCleaner v0.3 // Full System Intelligence Suite", font=get_font('body'), text_color=self.theme['dim']).pack()


if __name__ == "__main__":
    App().mainloop()
