#!/usr/bin/env python3
import sys
import os
from core.controller import CLIController
from ui.renderer import render_header, render_sys_info, render_menu, console, Panel
from ui.views import scan_view, process_view, optimizer_view

VERSION = "0.3.0.1"

def main():
    controller = CLIController()
    
    while True:
        os.system('clear')
        render_header(VERSION)
        
        info = controller.get_sys_info()
        render_sys_info(info)
        
        console.print("\n[bold]Main Menu[/bold]")
        options = [
            "Hyper Scan (Clean Junk)",
            "Process Sentinel (Task Manager)",
            "System Optimizer (RAM/Swap/Kernel)",
            "Developer Hub",
            "Update History",
            "Exit"
        ]
        render_menu(options)
        
        try:
            choice = console.input("\n[bold cyan]Select an option: [/bold cyan]")
            
            if choice == "1":
                scan_view(controller)
                console.input("\nPress Enter to return...")
            elif choice == "2":
                process_view(controller)
            elif choice == "3":
                optimizer_view(controller)
                console.input("\nPress Enter to return...")
            elif choice == "4":
                dev_hub(controller)
                console.input("\nPress Enter to return...")
            elif choice == "5":
                show_history()
                console.input("\nPress Enter to return...")
            elif choice == "6" or choice.lower() == 'q':
                console.print("[yellow]Exiting MLCleaner-CLI...[/yellow]")
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.input("\nPress Enter to continue...")

def dev_hub(controller):
    console.print("\n[bold cyan]Developer Hub[/bold cyan]")
    options = [
        "Docker System Prune",
        "Clear NPM Cache",
        "Purge Python PyCache",
        "Git GC (Aggressive)",
        "Wipe build/ dist/ artifacts",
        "Back"
    ]
    render_menu(options)
    choice = console.input("\nSelect tool: ")
    
    import subprocess
    if choice == "1":
        subprocess.run(["docker", "system", "prune", "-f"])
    elif choice == "2":
        subprocess.run(["npm", "cache", "clean", "--force"], shell=True)
    elif choice == "3":
        os.system("find . -name '__pycache__' -type d -exec rm -rf {} +")
        console.print("[green]PyCache purged.[/green]")
    elif choice == "4":
        subprocess.run(["git", "gc", "--prune=now", "--aggressive"])
    elif choice == "5":
        os.system("rm -rf build/ dist/ *.egg-info")
        console.print("[green]Build artifacts removed.[/green]")

def show_history():
    history_file = os.path.join(os.path.dirname(__file__), "UPDATE_LOG.txt")
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            from rich.markdown import Markdown
            console.print(Panel(Markdown(f.read()), title="[bold]Update Chronicles[/bold]", border_style="green"))
    else:
        console.print("[red]History log not found.[/red]")

if __name__ == "__main__":
    main()
