from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from .renderer import console, format_size, render_menu
import time

def scan_view(controller):
    console.print("\n[bold cyan]Starting Global Hyper-Scan...[/bold cyan]")
    
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Analyzing targets...", total=len(controller.engine.targets))
        
        def cb(pct, name):
            progress.update(task, completed=pct*len(controller.engine.targets), description=f"Analyzing: {name}")
            
        results = controller.engine.scan(callback_progress=cb)

    if not results:
        console.print("[yellow]No junk found.[/yellow]")
        return

    table = Table(title="Scan Discovery", box=None)
    table.add_column("Category", style="dim")
    table.add_column("Target", style="bold")
    table.add_column("Size", justify="right", style="green")

    total_size = sum(r['size'] for r in results)
    
    # Show top 50
    for r in results[:50]:
        table.add_row(r['type'], r['name'], format_size(r['size']))

    console.print(table)
    console.print(f"\n[bold green]TOTAL DISCOVERY: {format_size(total_size)}[/bold green]")
    
    choice = console.input("\n[bold]Clean all found items? (y/n/trash): [/bold]").lower()
    if choice in ['y', 'trash']:
        mode = 'trash' if choice == 'trash' else 'delete'
        count = controller.engine.clean(results, mode=mode)
        console.print(f"[bold green]Successfully processed {count} items.[/bold green]")

def process_view(controller):
    console.print("[dim]Press Ctrl+C to return to main menu[/dim]")
    try:
        with Live(console=console, screen=True, refresh_per_second=1) as live:
            while True:
                procs = controller.get_processes()[:25]
                table = Table(title="PROCESS SENTINEL (LIVE)", box=None, expand=True)
                table.add_column("PID", style="dim")
                table.add_column("NAME", style="bold white")
                table.add_column("CPU%", justify="right")
                table.add_column("RAM", justify="right")
                table.add_column("USER", style="dim")

                for p in procs:
                    color = "red" if p['cpu'] > 30 else "green"
                    table.add_row(
                        str(p['pid']),
                        p['name'],
                        f"[{color}]{p['cpu']:.1f}%[/{color}]",
                        format_size(p['ram']),
                        p['user']
                    )
                live.update(table)
                time.sleep(3)
    except KeyboardInterrupt:
        return

def optimizer_view(controller):
    console.print("\n[bold cyan]System Optimizer[/bold cyan]")
    options = [
        "Drop RAM Caches",
        "Refresh Swap",
        "Set Performance Profile (Gaming)",
        "Set Balanced Profile",
        "Back"
    ]
    
    render_menu(options)
    
    choice = console.input("\nSelect option: ")
    if choice == "1":
        success, msg = controller.optimizer.drop_caches()
        console.print(f"[{'green' if success else 'red'}]{msg}[/]")
    elif choice == "2":
        success, msg = controller.optimizer.optimize_swap()
        console.print(f"[{'green' if success else 'red'}]{msg}[/]")
    elif choice == "3":
        success, msg = controller.optimizer.set_governor("performance")
        console.print(f"[{'green' if success else 'red'}]{msg}[/]")
    elif choice == "4":
        success, msg = controller.optimizer.set_governor("balanced")
        console.print(f"[{'green' if success else 'red'}]{msg}[/]")
