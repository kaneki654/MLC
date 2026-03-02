THEMES = {
    "Cyberpunk": {
        "bg": "#0a0a0f",              # Darker blue-black
        "card": "#1a1a24",            # Visible elevation
        "card_hover": "#252530",      # Hover state
        "surface": "#14141c",         # Intermediate surface
        "accent": "#00f3ff",
        "accent2": "#bd00ff",
        "accent_dim": "#007a80",      # Dimmed accent
        "text": "#f0f0f5",
        "text_secondary": "#a0a0b0",  # Secondary text
        "dim": "#606075",
        "success": "#00ff9d",
        "warning": "#ffb800",
        "error": "#ff3366",
        "info": "#00a3ff",
        "border": "#2a2a35",
        "divider": "#1f1f28",
        # Glassmorphism
        "glass_bg": "#1a1a2466",
        "glass_border": "#ffffff15",
        "glass_highlight": "#ffffff08",
        # Gradients
        "gradient_start": "#0a0a0f",
        "gradient_end": "#14141c",
        # Glow colors
        "glow_primary": "#00f3ff40",
        "glow_secondary": "#bd00ff40",
    },
    "Matrix": {
        "bg": "#000000",
        "card": "#0a0a0a",
        "card_hover": "#141414",
        "surface": "#050505",
        "accent": "#00ff41",
        "accent2": "#008f11",
        "accent_dim": "#004d0f",
        "text": "#00ff41",
        "text_secondary": "#00cc33",
        "dim": "#003b00",
        "success": "#00ff41",
        "warning": "#ccff00",
        "error": "#ff4141",           # Fixed: red instead of green
        "info": "#00cc41",
        "border": "#0a2a0a",
        "divider": "#051505",
        # Glassmorphism
        "glass_bg": "#0a0a0a66",
        "glass_border": "#00ff4115",
        "glass_highlight": "#00ff4108",
        # Gradients
        "gradient_start": "#000000",
        "gradient_end": "#050505",
        # Glow colors
        "glow_primary": "#00ff4140",
        "glow_secondary": "#008f1140",
    },
    "Vaporwave": {
        "bg": "#2b213a",
        "card": "#241b35",
        "card_hover": "#342646",
        "surface": "#1e1630",
        "accent": "#ff71ce",          # Pink
        "accent2": "#01cdfe",         # Blue
        "accent_dim": "#b34d91",
        "text": "#ffffff",
        "text_secondary": "#c8c8d0",
        "dim": "#b967ff",
        "success": "#05ffa1",
        "warning": "#ffe66d",
        "error": "#ff6b6b",
        "info": "#01cdfe",
        "border": "#3d2e52",
        "divider": "#2f2340",
        # Glassmorphism
        "glass_bg": "#241b3566",
        "glass_border": "#ff71ce15",
        "glass_highlight": "#ffffff08",
        # Gradients
        "gradient_start": "#2b213a",
        "gradient_end": "#1e1630",
        # Glow colors
        "glow_primary": "#ff71ce40",
        "glow_secondary": "#01cdfe40",
    },
    "Red Alert": {
        "bg": "#1a0b0b",
        "card": "#2d1414",
        "card_hover": "#3d1c1c",
        "surface": "#241010",
        "accent": "#ff0000",
        "accent2": "#ff4444",
        "accent_dim": "#aa0000",
        "text": "#ffffff",
        "text_secondary": "#ffcccc",
        "dim": "#884444",
        "success": "#40ff40",         # Fixed: green for success
        "warning": "#ffaa00",
        "error": "#ff2020",           # Fixed: red for error
        "info": "#ff6666",
        "border": "#4a2020",
        "divider": "#3a1818",
        # Glassmorphism
        "glass_bg": "#2d141466",
        "glass_border": "#ff000015",
        "glass_highlight": "#ffffff08",
        # Gradients
        "gradient_start": "#1a0b0b",
        "gradient_end": "#241010",
        # Glow colors
        "glow_primary": "#ff000040",
        "glow_secondary": "#ff444440",
    },
    "Lite": {
        "bg": "#F2F2F2",
        "card": "#FFFFFF",
        "card_hover": "#E5E5E5",
        "surface": "#FFFFFF",
        "accent": "#000000",
        "accent2": "#666666",
        "accent_dim": "#333333",
        "text": "#000000",
        "text_secondary": "#444444",
        "dim": "#888888",
        "success": "#008000",
        "warning": "#808000",
        "error": "#800000",
        "info": "#000080",
        "border": "#CCCCCC",
        "divider": "#DDDDDD",
        "glass_bg": "#FFFFFF",
        "glass_border": "#CCCCCC",
        "glass_highlight": "#FFFFFF",
        "gradient_start": "#F2F2F2",
        "gradient_end": "#F2F2F2",
        "glow_primary": "#00000000",
        "glow_secondary": "#00000000",
    },
    "Deep Dark": {
        "bg": "#000000",
        "card": "#111111",
        "card_hover": "#1A1A1A",
        "surface": "#080808",
        "accent": "#FFFFFF",
        "accent2": "#AAAAAA",
        "accent_dim": "#666666",
        "text": "#FFFFFF",
        "text_secondary": "#CCCCCC",
        "dim": "#666666",
        "success": "#00FF00",
        "warning": "#FFFF00",
        "error": "#FF0000",
        "info": "#00FFFF",
        "border": "#222222",
        "divider": "#111111",
        "glass_bg": "#111111",
        "glass_border": "#222222",
        "glass_highlight": "#111111",
        "gradient_start": "#000000",
        "gradient_end": "#000000",
        "glow_primary": "#00000000",
        "glow_secondary": "#00000000",
    }
}

class ThemeManager:
    THEMES = THEMES

    def __init__(self):
        self.current = "Lite"

    def get(self):
        return THEMES[self.current]

    def set_theme(self, name):
        if name in THEMES:
            self.current = name
        return self.get()
