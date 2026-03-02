import customtkinter as ctk
import psutil
import os
import platform
from ui.design_system import SPACING, CARD, get_font, ICONS, format_size

class InfoView(ctk.CTkFrame):
    def __init__(self, master, worker, theme):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="🏥  SYSTEM INFORMATION", font=get_font('h1'), text_color=self.theme['accent']).pack(side="left")
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # 1. OS Info
        os_frame = self._create_card(scroll, "OPERATING SYSTEM")
        self._add_info_row(os_frame, "Distro", platform.platform())
        self._add_info_row(os_frame, "Kernel", platform.release())
        self._add_info_row(os_frame, "Arch", platform.machine())

        # 2. CPU Info
        cpu_frame = self._create_card(scroll, "PROCESSOR (CPU)")
        # Get CPU model (linux specific)
        model = "N/A"
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        model = line.split(":")[1].strip()
                        break
        except: pass
        self._add_info_row(cpu_frame, "Model", model)
        self._add_info_row(cpu_frame, "Cores", f"{psutil.cpu_count(logical=False)} Physical / {psutil.cpu_count(logical=True)} Logical")
        
        # 3. Memory Info
        mem_frame = self._create_card(scroll, "MEMORY (RAM)")
        vm = psutil.virtual_memory()
        self._add_info_row(mem_frame, "Total", format_size(vm.total))
        self._add_info_row(mem_frame, "Type", "Unknown/DDR") # psutil doesn't give type easily

        # 4. Storage Info
        disk_frame = self._create_card(scroll, "STORAGE DRIVES")
        for part in psutil.disk_partitions():
            if 'loop' in part.device or 'snap' in part.mountpoint: continue
            try:
                u = psutil.disk_usage(part.mountpoint)
                self._add_info_row(disk_frame, f"Device ({part.device})", f"{format_size(u.total)} [{part.fstype}]")
            except: pass

    def _create_card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        card.pack(fill="x", pady=10)
        ctk.CTkLabel(card, text=title, font=get_font('h3'), text_color=self.theme['accent']).pack(anchor="w", padx=20, pady=10)
        return card

    def _add_info_row(self, card, label, value):
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=f"{label}:", font=get_font('label'), width=120, anchor="w").pack(side="left")
        ctk.CTkLabel(row, text=value, font=get_font('body'), text_color=self.theme['text']).pack(side="left")
