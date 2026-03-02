# Design System - Professional Pro Suite v3.3 High Visibility

# Basic spacing (8px grid)
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
    'page': 25,
}

# Icons (Unicode Glyphs for zero overhead)
ICONS = {
    'menu': '☰',
    'dashboard': '📊',
    'scan': '🔍',
    'files': '📁',
    'tools': '🛠',
    'dev': '👨‍💻',
    'settings': '⚙',
    'trash': '🗑',
    'back': '⬅',
    'check': '✅',
    'error': '❌',
    'info': 'ℹ',
    'docker': '🐳',
    'node': '📦',
    'python': '🐍',
    'git': '🌿',
    'cloud': '☁',
    'gear': '⚙',
    'web': '🌐',
    'activity': '⚡'
}

# Typography - HIGH VISIBILITY BOLD
TYPOGRAPHY = {
    'h1': ('sans-serif', 26, 'bold'),
    'h2': ('sans-serif', 21, 'bold'),
    'h3': ('sans-serif', 17, 'bold'),
    'h4': ('sans-serif', 15, 'bold'),
    'body': ('sans-serif', 14, 'bold'), # Forced bold for visibility
    'label': ('sans-serif', 12, 'bold'),
    'mono': ('monospace', 11, 'bold'),
}

# Sidebar tokens
SIDEBAR = {
    'width': 70,
}

CARD = {
    'corner_radius': 6,
    'corner_radius_sm': 4,
    'border_width': 2, # Defined borders for visibility
    'graph_height': 120, # Fixed missing graph height
}

def get_font(style):
    font = TYPOGRAPHY.get(style, TYPOGRAPHY['body'])
    return (font[0], font[1], font[2]) if len(font) > 2 else (font[0], font[1])

def format_size(size_bytes):
    """Formats bytes to the most appropriate unit, supporting up to TB."""
    if size_bytes == 0: return "0 B"
    units = ("B", "KB", "MB", "GB", "TB", "PB")
    import math
    try:
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {units[i]}"
    except:
        return f"{size_bytes} B"
