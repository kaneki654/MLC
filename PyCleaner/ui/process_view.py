import customtkinter as ctk
import threading
import time
from tkinter import messagebox
from ui.design_system import SPACING, CARD, get_font, ICONS, format_size

class ProcessView(ctk.CTkFrame):
    def __init__(self, master, worker, theme):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self.processes = []
        self.active = False
        self.search_query = ""
        self.row_widgets = {} # pid -> {'frame': CTkFrame, 'cpu_lbl': CTkLabel, 'ram_lbl': CTkLabel, 'status_lbl': CTkLabel}
        
        self._setup_ui()

    def _setup_ui(self):
        # Header with Search and Boost
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(header, text=f"{ICONS['activity']}  PROCESS SENTINEL", font=get_font('h1'), text_color=self.theme['accent']).pack(side="left")
        
        self.boost_btn = ctk.CTkButton(header, text="SYSTEM BOOST", font=get_font('h4'), 
                                      fg_color=self.theme['error'], text_color="#FFFFFF",
                                      width=150, height=40, command=self.manual_boost)
        self.boost_btn.pack(side="right", padx=(10, 0))

        # Search Bar
        self.search_ent = ctk.CTkEntry(header, placeholder_text="Search processes...", height=40, font=get_font('body'),
                                      fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        self.search_ent.pack(side="right", fill="x", expand=True, padx=10)
        self.search_ent.bind("<KeyRelease>", self._on_search)

        # Process Table Header
        self.table_header = ctk.CTkFrame(self, fg_color=self.theme['surface'], height=40, corner_radius=CARD['corner_radius_sm'])
        self.table_header.pack(fill="x", pady=(0, 5))
        self.table_header.pack_propagate(False)
        
        # Grid weights for alignment
        cols = [("NAME", 0.4), ("PID", 0.1), ("CPU %", 0.15), ("RAM", 0.15), ("STATUS", 0.2)]
        for text, weight in cols:
            lbl = ctk.CTkLabel(self.table_header, text=text, font=get_font('label'), text_color=self.theme['dim'])
            lbl.place(relx=sum(c[1] for c in cols[:cols.index((text, weight))]), rely=0.5, anchor="w", x=15)

        # Process List
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        self.scroll.pack(fill="both", expand=True)

    def _on_search(self, event):
        self.search_query = self.search_ent.get().lower()
        self.refresh_list()

    def _create_row(self, index):
        row = ctk.CTkFrame(self.scroll, fg_color="transparent", height=45)
        row.grid(row=index, column=0, sticky="ew", pady=1)
        row.grid_columnconfigure(0, weight=1)
        
        # We need a container inside for the layout bits
        inner = ctk.CTkFrame(row, fg_color="transparent", height=45)
        inner.pack(fill="both", expand=True)

        # Name & Indicator
        name_lbl = ctk.CTkLabel(inner, text="", font=get_font('body'))
        name_lbl.place(relx=0, rely=0.5, anchor="w", x=10)
        
        # PID
        pid_lbl = ctk.CTkLabel(inner, text="", font=get_font('mono'), text_color=self.theme['dim'])
        pid_lbl.place(relx=0.4, rely=0.5, anchor="w", x=15)
        
        # CPU
        cpu_lbl = ctk.CTkLabel(inner, text="", font=get_font('body'))
        cpu_lbl.place(relx=0.5, rely=0.5, anchor="w", x=15)
        
        # RAM
        ram_lbl = ctk.CTkLabel(inner, text="", font=get_font('body'))
        ram_lbl.place(relx=0.65, rely=0.5, anchor="w", x=15)
        
        # Status
        status_lbl = ctk.CTkLabel(inner, text="", font=get_font('label'), text_color=self.theme['dim'])
        status_lbl.place(relx=0.8, rely=0.5, anchor="w", x=15)

        # Actions
        kill_btn = ctk.CTkButton(inner, text=ICONS['trash'], width=30, height=30, 
                                fg_color="transparent", text_color=self.theme['error'],
                                font=get_font('h3'))
        kill_btn.pack(side="right", padx=10)
        
        info_btn = ctk.CTkButton(inner, text=ICONS['info'], width=30, height=30,
                                fg_color="transparent", text_color=self.theme['accent'],
                                font=get_font('h3'))
        info_btn.pack(side="right", padx=2)

        self.row_widgets[index] = {
            'frame': row,
            'name_lbl': name_lbl,
            'pid_lbl': pid_lbl,
            'cpu_lbl': cpu_lbl,
            'ram_lbl': ram_lbl,
            'status_lbl': status_lbl,
            'kill_btn': kill_btn,
            'info_btn': info_btn
        }

    def refresh_list(self):
        filtered = [p for p in self.processes if self.search_query in p['name'].lower() or self.search_query in str(p['pid'])]
        filtered.sort(key=lambda x: x['cpu'], reverse=True)
        
        text_col = "#FFFFFF" if self.theme.get('bg') != "#F2F2F2" else "#000000"

        # Configure scroll container
        self.scroll.grid_columnconfigure(0, weight=1)

        for i, p in enumerate(filtered[:80]): # Reduced limit slightly for better perf
            if i not in self.row_widgets:
                self._create_row(i)
            
            w = self.row_widgets[i]
            w['frame'].grid(row=i, column=0, sticky="ew", pady=1)
            
            status_color = self.theme['success'] if p['cpu'] < 10 else (self.theme['warning'] if p['cpu'] < 40 else self.theme['error'])
            
            w['name_lbl'].configure(text=f"• {p['name']}", text_color=text_col)
            w['pid_lbl'].configure(text=str(p['pid']))
            w['cpu_lbl'].configure(text=f"{p['cpu']:.1f}%", text_color=status_color)
            w['ram_lbl'].configure(text=format_size(p['ram']), text_color=text_col)
            w['status_lbl'].configure(text=p['status'].upper())
            
            # Fix button commands
            w['kill_btn'].configure(command=lambda pid=p['pid']: self.kill_request(pid))
            w['info_btn'].configure(command=lambda proc=p: self.show_details(proc))

        # Hide unused rows
        for i in range(len(filtered), len(self.row_widgets)):
            if i in self.row_widgets:
                self.row_widgets[i]['frame'].grid_forget()

    def kill_request(self, pid):
        if messagebox.askyesno("Terminate Process", f"Are you sure you want to end process {pid}?"):
            success, msg = self.worker.kill_process(pid)
            if not success:
                messagebox.showerror("Error", msg)
            self._update_data()

    def show_details(self, p):
        details = f"Name: {p['name']}\nPID: {p['pid']}\nUser: {p['user']}\nCPU: {p['cpu']:.1f}%\nRAM: {format_size(p['ram'])}\nStatus: {p['status']}\nUptime: {int(p['uptime'])}s\n\nCommand:\n{p['cmd']}"
        messagebox.showinfo("Process Details", details)

    def manual_boost(self):
        # Find user apps consuming > 1% CPU or > 100MB RAM
        candidates = []
        for p in self.processes:
            if p['user'] and p['user'] != 'root':
                if p['cpu'] > 1.0 or p['ram'] > 100 * 1024 * 1024:
                    if p['name'].lower() not in ['python', 'mlcleaner', 'bash', 'xorg', 'gnome-shell']:
                        candidates.append(p)
        
        if not candidates:
            messagebox.showinfo("System Boost", "No heavy user processes found to optimize.")
            return

        boost_msg = "Identify heavy processes to terminate:\n\n"
        for i, p in enumerate(candidates[:10]):
            boost_msg += f"[{i+1}] {p['name']} ({format_size(p['ram'])})\n"
        
        if messagebox.askyesno("Manual Boost", boost_msg + "\nWould you like to terminate these processes?"):
            count = 0
            for p in candidates:
                self.worker.kill_process(p['pid'], force=True)
                count += 1
            messagebox.showinfo("Boost Complete", f"Terminated {count} processes.")
            self._update_data()

    def start_loop(self):
        self.active = True
        self._loop()

    def stop_loop(self):
        self.active = False

    def _loop(self):
        if not self.active: return
        self._update_data()
        # Refresh every 3 seconds for AMD A4
        self.after(3000, self._loop)

    def _update_data(self):
        def _fetch():
            self.processes = self.worker.get_processes()
            self.after(0, self.refresh_list)
        threading.Thread(target=_fetch, daemon=True).start()
