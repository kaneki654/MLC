# Lightweight UI Components - High Visibility Edition
import customtkinter as ctk
from ui.design_system import CARD, SPACING, get_font

class GlassCard(ctk.CTkFrame):
    """Simplified Card for performance with high contrast."""
    def __init__(self, master, theme, **kwargs):
        kwargs.setdefault('fg_color', theme['card'])
        kwargs.setdefault('corner_radius', CARD['corner_radius'])
        kwargs.setdefault('border_width', CARD['border_width'])
        kwargs.setdefault('border_color', theme['border'])
        super().__init__(master, **kwargs)

class IconButton(ctk.CTkButton):
    def __init__(self, master, text="", theme=None, **kwargs):
        if theme:
            # Force high contrast text - Pure White for Dark Themes
            is_lite = theme.get('bg') == "#F2F2F2"
            text_col = "#000000" if is_lite else "#FFFFFF"
            kwargs.setdefault('fg_color', theme['card'])
            kwargs.setdefault('hover_color', theme['surface'])
            kwargs.setdefault('text_color', text_col)
        kwargs.setdefault('corner_radius', CARD['corner_radius_sm'])
        kwargs.setdefault('border_width', 2)
        kwargs.setdefault('font', get_font('body'))
        super().__init__(master, text=text, **kwargs)

class ToolCard(ctk.CTkFrame):
    def __init__(self, master, theme, title, subtitle, command=None, **kwargs):
        # Use solid borders for visibility
        super().__init__(master, fg_color=theme['card'], border_width=CARD['border_width'], 
                         border_color=theme['border'], corner_radius=CARD['corner_radius'], **kwargs)
        self.command = command
        
        lbl_frame = ctk.CTkFrame(self, fg_color="transparent")
        lbl_frame.pack(expand=True, padx=15, pady=15)
        
        # High contrast white text for dark modes
        is_lite = theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        
        ctk.CTkLabel(lbl_frame, text=title, font=get_font('h3'), text_color=text_col).pack()
        ctk.CTkLabel(lbl_frame, text=subtitle, font=get_font('body'), text_color=theme['dim']).pack(pady=(5, 0))
        
        if command:
            self.bind("<Button-1>", lambda e: command())
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: command())

class ThemeButton(ctk.CTkButton):
    def __init__(self, master, theme, theme_name, command=None, **kwargs):
        is_lite = theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        super().__init__(master, text=theme_name, command=command, 
                         fg_color=theme['surface'], text_color=text_col,
                         border_width=2, border_color=theme['border'], 
                         font=get_font('body'), **kwargs)

class PasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.password = None
        self.theme = theme
        
        # Window setup
        self.title("Authentication Required")
        self.geometry("400x220")
        self.resizable(False, False)
        self.transient(parent) # Keep on top of parent
        
        # Center the window
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 110
        self.geometry(f"+{x}+{y}")
        
        self.configure(fg_color=theme['bg'])
        
        # Determine text color
        is_lite = theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        
        # Content
        ctk.CTkLabel(self, text="🔒 System Access Required", font=get_font('h3'), text_color=theme['accent']).pack(pady=(20, 10))
        ctk.CTkLabel(self, text="Enter your sudo password to perform this action.", font=get_font('body'), text_color=text_col).pack(pady=(0, 15))
        
        self.entry = ctk.CTkEntry(self, show="•", width=250, height=40, font=get_font('body'))
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self.confirm)
        self.entry.focus_set()
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Cancel", fg_color=theme['surface'], text_color=text_col, 
                     width=100, border_width=2, border_color=theme['border'],
                     command=self.cancel).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="Authenticate", fg_color=theme['accent'], text_color="black", 
                     width=120, command=self.confirm).pack(side="left", padx=10)
        
        self.after(100, lambda: self.grab_set()) # Safe grab
        self.wait_window()

    def confirm(self, event=None):
        self.password = self.entry.get()
        self.destroy()

    def cancel(self):
        self.password = None
        self.destroy()
