import customtkinter as ctk
import os
import threading
import subprocess
from tkinter import messagebox, filedialog
from ui.design_system import SPACING, CARD, get_font, ICONS, format_size

class ToolboxView(ctk.CTkFrame):
    def __init__(self, master, worker, theme):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))
        ctk.CTkLabel(header, text=f"{ICONS['tools']}  TOOLBOX UTILITIES", font=get_font('h1'), text_color=self.theme['accent']).pack(side="left")
        
        # Tabs
        self.tabs = ctk.CTkFrame(self, fg_color="transparent")
        self.tabs.pack(fill="x", pady=(0, 15))
        
        self.tab_btns = []
        for name in ["SCAN", "DUPLICATES", "SNAPSHOTS", "NET CHECK"]:
            btn = ctk.CTkButton(self.tabs, text=name, width=140, height=40,
                               fg_color=self.theme['card'], text_color=self.theme['text'],
                               hover_color=self.theme['surface'], corner_radius=CARD['corner_radius_sm'],
                               border_width=1, border_color=self.theme['border'],
                               font=get_font('label'),
                               command=lambda n=name: self.switch_tab(n))
            btn.pack(side="left", padx=8)
            self.tab_btns.append(btn)

        self.container = ctk.CTkFrame(self, fg_color=self.theme['card'], border_width=CARD['border_width'], border_color=self.theme['border'])
        self.container.pack(fill="both", expand=True)
        
        self.switch_tab("SCAN")

    def switch_tab(self, name):
        for btn in self.tab_btns:
            if btn.cget("text") == name: 
                btn.configure(fg_color=self.theme['accent'], text_color=self.theme['bg'], border_width=0)
            else: 
                btn.configure(fg_color=self.theme['card'], text_color=self.theme['text'], border_width=1)
            
        for w in self.container.winfo_children(): w.destroy()
        
        if name == "SCAN": self.show_large()
        elif name == "DUPLICATES": self.show_dupes()
        elif name == "SNAPSHOTS": self.show_snaps()
        elif name == "NET CHECK": self.show_net()

    def show_large(self):
        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        loading = ctk.CTkLabel(scroll, text="Scanning for large files (50MB+)...", font=get_font('h4'), text_color=self.theme['dim'])
        loading.pack(pady=40)
        
        def run():
            try:
                res = self.worker.analyzer.find_large_files("/", min_size_mb=50)
                self.after(0, lambda: self._render_list(scroll, res, loading))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Tool Error", str(e)))
                
        threading.Thread(target=run, daemon=True).start()

    def _render_list(self, scroll, res, loading_lbl):
        try:
            if not scroll.winfo_exists(): return
            loading_lbl.destroy()
        except: return

        if not res:
            ctk.CTkLabel(scroll, text="No large files found.", font=get_font('body')).pack(pady=40)
            return

        for item in res:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=4, padx=10)
            sz_str = format_size(item['size'])
            ctk.CTkLabel(row, text=f"[{sz_str}]", font=get_font('label'), text_color=self.theme['accent'], width=100).pack(side="left")
            name = item['name']
            if len(name) > 60: name = name[:57] + "..."
            ctk.CTkLabel(row, text=name, font=get_font('body'), text_color=self.theme['text']).pack(side="left", padx=15)
            ctk.CTkButton(row, text=ICONS['trash'], width=35, height=30, fg_color="transparent", 
                         text_color=self.theme['error'], font=get_font('h4'),
                         command=lambda p=item['path'], r=row: self.delete(p, r)).pack(side="right")

    def show_dupes(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(f, text="DUPLICATE ENGINE", font=get_font('h2'), text_color=self.theme['accent']).pack(anchor="w")
        ctk.CTkLabel(f, text="Analyzes your HOME directory using MD5 fingerprinting (Optimized for AMD A4).", font=get_font('body'), text_color=self.theme['dim']).pack(anchor="w", pady=(5, 30))
        
        self.dupe_res = ctk.CTkScrollableFrame(f, fg_color=self.theme['surface'], height=300)
        self.dupe_res.pack(fill="both", expand=True, pady=(0, 20))
        
        self.prog_lbl = ctk.CTkLabel(f, text="Select directory and start scan.", font=get_font('body'))
        self.prog_lbl.pack(pady=5)
        
        btn_box = ctk.CTkFrame(f, fg_color="transparent")
        btn_box.pack(fill="x")
        
        ctk.CTkButton(btn_box, text="START HOME SCAN", height=45, fg_color=self.theme['accent'], text_color=self.theme['bg'],
                           command=self.run_dupe_scan).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_box, text="SELECT FOLDER", height=45, fg_color=self.theme['surface'], text_color=self.theme['text'],
                           command=self.select_folder_dupe).pack(side="left", expand=True, padx=5)

    def select_folder_dupe(self):
        p = filedialog.askdirectory()
        if p: self.run_dupe_scan(p)

    def run_dupe_scan(self, path=None):
        if not path: path = os.path.expanduser("~")
        for w in self.dupe_res.winfo_children(): w.destroy()
        
        def run():
            def progress(p, msg):
                self.after(0, lambda: self.prog_lbl.configure(text=f"[{int(p*100)}%] {msg}"))
            
            res = self.worker.analyzer.find_duplicates(path, progress)
            self.after(0, self._render_dupes, res)
            
        threading.Thread(target=run, daemon=True).start()

    def _render_dupes(self, res):
        self.prog_lbl.configure(text=f"Scan complete. Found {len(res)} duplicate sets.")
        if not res:
            ctk.CTkLabel(self.dupe_res, text="No duplicates found.", font=get_font('body')).pack(pady=40)
            return

        for item in res:
            group = ctk.CTkFrame(self.dupe_res, fg_color=self.theme['card'], border_width=1, border_color=self.theme['border'])
            group.pack(fill="x", pady=8, padx=5)
            
            header = ctk.CTkFrame(group, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(header, text=f"DUPLICATE SET ({format_size(item['size'])})", font=get_font('label'), text_color=self.theme['accent']).pack(side="left")
            
            # Show all paths in set
            for i, p in enumerate(item['paths']):
                row = ctk.CTkFrame(group, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=2)
                
                # Highlight all except the first one? No, let user choose.
                # Usually we want to keep one.
                col = self.theme['dim'] if i == 0 else self.theme['text']
                ctk.CTkLabel(row, text=p, font=get_font('small'), text_color=col, wraplength=500, justify="left").pack(side="left")
                
                ctk.CTkButton(row, text=ICONS['trash'], width=30, height=25, fg_color="transparent", 
                             text_color=self.theme['error'], font=get_font('body'),
                             command=lambda path=p, r=row: self.delete(path, r)).pack(side="right")

    def show_snaps(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(f, text="ZERO-SPACE SNAPSHOTS", font=get_font('h2'), text_color=self.theme['accent']).pack(anchor="w")
        ctk.CTkLabel(f, text="Instantly backup any folder. Uses hard-links to consume 0 bytes of extra space.", font=get_font('body'), text_color=self.theme['dim']).pack(anchor="w", pady=(5, 25))
        
        self.src_ent = ctk.CTkEntry(f, placeholder_text="Select source directory...", height=45, fg_color=self.theme['surface'])
        self.src_ent.pack(fill="x", pady=15)
        
        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(fill="x")
        ctk.CTkButton(btns, text="BROWSE FOLDER", height=40, command=self.browse).pack(side="left", padx=(0, 15))
        ctk.CTkButton(btns, text="CREATE SNAPSHOT", height=40, fg_color=self.theme['accent'], text_color=self.theme['bg'], command=self.create).pack(side="left")

    def browse(self):
        p = filedialog.askdirectory()
        if p:
            self.src_ent.delete(0, 'end')
            self.src_ent.insert(0, p)

    def create(self):
        p = self.src_ent.get()
        if p and os.path.exists(p):
            root = os.path.join(os.path.expanduser("~"), ".mlcleaner_snapshots")
            os.makedirs(root, exist_ok=True)
            success, msg = self.worker.create_snapshot(p, root)
            messagebox.showinfo("Toolbox", msg)

    def delete(self, path, row):
        if messagebox.askyesno("Confirm Deletion", f"Permanently remove file?\n{path}"):
            try:
                if os.path.exists(path):
                    os.remove(path)
                row.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")

    def show_net(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=25)
        ctk.CTkLabel(f, text="NETWORK DIAGNOSTIC", font=get_font('h2'), text_color=self.theme['accent']).pack(anchor="w")
        ctk.CTkLabel(f, text="Check connectivity and latency to global DNS.", font=get_font('body'), text_color=self.theme['dim']).pack(anchor="w", pady=(5, 25))
        
        self.net_out = ctk.CTkTextbox(f, font=get_font('mono'), text_color=self.theme['text'], fg_color=self.theme['surface'])
        self.net_out.pack(fill="both", expand=True, pady=(0, 10))
        
        def run_ping():
            self.net_out.delete("0.0", "end")
            self.net_out.insert("end", "Pinging 8.8.8.8...\n")
            try:
                param = '-n' if os.name == 'nt' else '-c'
                cmd = ['ping', param, '4', '8.8.8.8']
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                output = stdout if stdout else stderr
                self.after(0, lambda: self.net_out.insert("end", output))
            except Exception as e:
                self.after(0, lambda: self.net_out.insert("end", f"Error: {e}"))

        ctk.CTkButton(f, text="PING GOOGLE (8.8.8.8)", height=40, fg_color=self.theme['accent'], text_color=self.theme['bg'],
                     command=lambda: threading.Thread(target=run_ping, daemon=True).start()).pack(anchor="w")
