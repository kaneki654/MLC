import customtkinter as ctk
import threading
from tkinter import messagebox
from ui.design_system import SPACING, CARD, get_font, ICONS, format_size

class ScanView(ctk.CTkFrame):
    def __init__(self, master, worker, theme, low_power_mode=True):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self.results = []
        self.category_vars = {}
        # Support for different master levels
        self.app = self.winfo_toplevel()
        self._setup_ui()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))
        ctk.CTkLabel(header, text=f"{ICONS['scan']}  SYSTEM HYPER-SCAN", font=get_font('h1'), text_color=self.theme['accent']).pack(side="left")

        # Initial Card
        self.card = ctk.CTkFrame(self, fg_color=self.theme['card'], border_width=CARD['border_width'], border_color=self.theme['border'])
        self.card.pack(expand=True, padx=50, pady=50)
        
        # High visibility text color based on theme
        is_lite = self.theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        
        ctk.CTkLabel(self.card, text="Analyze 300+ system targets", font=get_font('h3'), text_color=text_col).pack(pady=35, padx=50)
        
        self.main_btn = ctk.CTkButton(self.card, text="START SCAN", font=get_font('h4'),
                                     fg_color=self.theme['accent'], text_color=self.theme['bg'],
                                     height=55, width=220, command=self.start_scan)
        self.main_btn.pack(pady=(0, 35))

    def start_scan(self):
        for w in self.card.winfo_children(): w.destroy()
        
        self.pbar = ctk.CTkProgressBar(self.card, width=450, height=12, 
                                      progress_color=self.theme['accent'], fg_color=self.theme['surface'])
        self.pbar.pack(pady=35, padx=50)
        self.pbar.set(0)
        
        is_lite = self.theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        self.status = ctk.CTkLabel(self.card, text="Scanning...", font=get_font('body'), text_color=text_col)
        self.status.pack(pady=(0, 35))
        
        def run():
            try:
                def progress(p, n):
                    self.after(0, lambda: self.pbar.set(p))
                    self.after(0, lambda: self.status.configure(text="Scanning..."))
                    
                self.results = self.worker.engine.scan(callback_progress=progress)
                self.after(0, self.show_results)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Engine Error", f"Scan failed: {str(e)}"))
            
        threading.Thread(target=run, daemon=True).start()

    def show_results(self):
        for w in self.winfo_children(): w.destroy()
        
        is_lite = self.theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        
        # Results Header
        header = ctk.CTkFrame(self, fg_color=self.theme['card'], border_width=CARD['border_width'], border_color=self.theme['border'])
        header.pack(fill="x", pady=(0, 15))
        
        self.summary_label = ctk.CTkLabel(header, text="", font=get_font('h3'), text_color=self.theme['accent'])
        self.summary_label.pack(side="left", padx=25, pady=20)
        
        # Trash Toggle
        self.trash_var = ctk.BooleanVar(value=True)
        trash_switch = ctk.CTkSwitch(header, text="Move to Trash", variable=self.trash_var, 
                                    text_color=text_col, command=self.update_btn_text)
        trash_switch.pack(side="right", padx=15)

        self.action_btn = ctk.CTkButton(header, text="MOVE TO TRASH", font=get_font('h4'), fg_color=self.theme['error'], 
                     text_color="white", height=40, width=180, command=self.clean)
        self.action_btn.pack(side="right", padx=10)

        scroll = ctk.CTkScrollableFrame(self, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'])
        scroll.pack(fill="both", expand=True)
        
        # Group by category
        cats = {}
        for r in self.results:
            cat = r.get('type', 'OTHER')
            if cat not in cats: cats[cat] = []
            cats[cat].append(r)
            
        self.category_vars = {}
        
        for cat, items in cats.items():
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", pady=8)
            
            # Category Toggle
            cat_var = ctk.BooleanVar(value=True)
            self.category_vars[cat] = cat_var
            
            chk = ctk.CTkCheckBox(f, text=cat, variable=cat_var, 
                                 font=get_font('label'), text_color=self.theme['accent'],
                                 command=self.update_summary)
            chk.pack(anchor="w", padx=15)
            
            for item in items[:30]: 
                row = ctk.CTkFrame(f, fg_color="transparent")
                row.pack(fill="x", padx=45, pady=1) # Indented
                
                desc = item.get('description', '')
                name_text = f"• {item['name']} ({desc})" if desc else f"• {item['name']}"
                if len(name_text) > 80: name_text = name_text[:77] + "..."
                
                ctk.CTkLabel(row, text=name_text, font=get_font('body'), text_color=text_col).pack(side="left")
                ctk.CTkLabel(row, text=format_size(item['size']), font=get_font('label'), text_color=self.theme['dim']).pack(side="right")
            
            if len(items) > 30:
                ctk.CTkLabel(f, text=f"... and {len(items)-30} more items", font=get_font('body'), text_color=self.theme['dim']).pack(anchor="w", padx=60)

        self.update_summary()

    def update_summary(self):
        total_size = 0
        count = 0
        for item in self.results:
            cat = item.get('type', 'OTHER')
            if self.category_vars.get(cat) and self.category_vars[cat].get():
                total_size += item['size']
                count += 1
        
        size_str = format_size(total_size)
        self.summary_label.configure(text=f"Selected: {count} items ({size_str})")

    def update_btn_text(self):
        if self.trash_var.get():
            self.action_btn.configure(text="MOVE TO TRASH", fg_color=self.theme['accent'])
        else:
            self.action_btn.configure(text="PERMANENTLY DELETE", fg_color=self.theme['error'])

    def clean(self):
        # Filter selected items
        selected_items = []
        for item in self.results:
            cat = item.get('type', 'OTHER')
            if self.category_vars.get(cat) and self.category_vars[cat].get():
                selected_items.append(item)
                
        if not selected_items: return

        mode = 'trash' if self.trash_var.get() else 'delete'
        action_name = "move to Trash" if mode == 'trash' else "permanently delete"
        
        if not messagebox.askyesno("Confirm Action", f"Are you sure you want to {action_name} {len(selected_items)} items?"):
            return
            
        def run():
            try:
                # Use updated clean method with mode
                count = self.worker.engine.clean(selected_items, mode=mode)
                self.after(0, lambda: messagebox.showinfo("Success", f"Processed {count} items."))
                if hasattr(self.app, 'show_dashboard'):
                    self.after(0, self.app.show_dashboard)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", str(e)))
                
        threading.Thread(target=run, daemon=True).start()
