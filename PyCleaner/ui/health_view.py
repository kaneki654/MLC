import customtkinter as ctk
import os
from tkinter import messagebox
from ui.design_system import SPACING, CARD, get_font, ICONS

class HealthView(ctk.CTkFrame):
    def __init__(self, master, worker, theme):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="🏥 HEALTH & SECURITY", font=get_font('h1'), text_color=self.theme['accent']).pack(side="left")

        # Disk Health
        disk_frame = ctk.CTkFrame(self, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        disk_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(disk_frame, text="DISK SMART MONITOR", font=get_font('h3')).pack(anchor="w", padx=20, pady=15)
        
        drives = self.worker.health.get_disk_health()
        for d in drives:
            row = ctk.CTkFrame(disk_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(row, text=d['drive'], font=get_font('body')).pack(side="left")
            col = self.theme['success'] if d['status'] == "HEALTHY" else self.theme['error']
            ctk.CTkLabel(row, text=d['status'], font=get_font('body'), text_color=col).pack(side="right")

        # Security/Permissions
        sec_frame = ctk.CTkFrame(self, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        sec_frame.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(sec_frame, text="PERMISSION ANALYZER", font=get_font('h3')).pack(anchor="w", padx=20, pady=15)
        
        self.risk_scroll = ctk.CTkScrollableFrame(sec_frame, fg_color="transparent")
        self.risk_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkButton(sec_frame, text="SCAN FOR PERMISSION RISKS", command=self.scan_permissions).pack(pady=10)

    def scan_permissions(self):
        for w in self.risk_scroll.winfo_children(): w.destroy()
        
        loading = ctk.CTkLabel(self.risk_scroll, text="Analyzing permissions...", font=get_font('body'), text_color=self.theme['dim'])
        loading.pack(pady=20)
        self.update_idletasks() # Force render
        
        risks = self.worker.health.scan_unsafe_permissions(os.path.expanduser("~"))
        loading.destroy()
        
        if not risks:
            ctk.CTkLabel(self.risk_scroll, text="No immediate permission risks found in Home.", font=get_font('body')).pack()
        for r in risks[:20]:
            row = ctk.CTkFrame(self.risk_scroll, fg_color="transparent")
            row.pack(fill="x")
            ctk.CTkLabel(row, text=f"⚠️ {r['name']}", font=get_font('body'), text_color=self.theme['warning']).pack(side="left")
            ctk.CTkButton(row, text="FIX", width=60, height=20, command=lambda p=r['path']: self.fix_perm(p)).pack(side="right")

    def fix_perm(self, path):
        try:
            os.chmod(path, 0o644)
            messagebox.showinfo("Security", "Permission hardened to 644.")
        except: pass
