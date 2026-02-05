from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich import box

console = Console()

def render_header(version="0.3.0.1"):
    panel = Panel(
        f"[bold cyan]MLCLEANER[/bold cyan] [white]v{version}[/white]\n"
        "[dim]System Intelligence & Optimization Suite[/dim]",
        box=box.DOUBLE,
        border_style="blue"
    )
    console.print(panel)

def render_sys_info(info):
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_row("CPU Usage:", f"[bold {get_color(info['cpu_percent'])}]{info['cpu_percent']}%[/bold {get_color(info['cpu_percent'])}]")
    table.add_row("RAM Usage:", f"[bold {get_color(info['ram_percent'])}]{info['ram_percent']}%[/bold {get_color(info['ram_percent'])}]")
    table.add_row("System Load:", f"[bold]{info['load_avg'][0]:.2f}[/bold]")
    
    console.print(Panel(table, title="[bold]System Status[/bold]", border_style="cyan", expand=False))

def get_color(percent):
    if percent < 40: return "green"
    if percent < 80: return "yellow"
    return "red"

def render_menu(options):
    table = Table(box=box.MINIMAL, show_header=False, padding=(0, 1))
    for i, opt in enumerate(options, 1):
        table.add_row(f"[bold cyan]{i}.[/bold cyan]", opt)
    console.print(table)

def format_size(size_bytes):
    if size_bytes == 0: return "0 B"
    units = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {units[i]}"
