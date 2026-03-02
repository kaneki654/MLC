import customtkinter as ctk
import os
import subprocess
from tkinter import messagebox
from ui.design_system import get_font, ICONS, SPACING

class DevHubView(ctk.CTkFrame):
    def __init__(self, master, worker, theme):
        super().__init__(master, fg_color="transparent")
        self.worker = worker
        self.theme = theme
        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text=f"{ICONS['dev']}  DEVELOPER COMMAND CENTER", font=get_font('h1'), text_color=self.theme['accent']).pack(side="left")
        
        # Professional Tabview
        self.tabs = ctk.CTkTabview(self, fg_color=self.theme['card'], border_width=2, border_color=self.theme['border'], corner_radius=8)
        self.tabs.pack(fill="both", expand=True)
        
        self.tabs.add("VIRTUAL")
        self.tabs.add("WEB/JS")
        self.tabs.add("PYTHON")
        self.tabs.add("BUILD")
        self.tabs.add("CLOUD/IDE")
        self.tabs.add("GIT")

        home = os.path.expanduser('~')

        # Tab: VIRTUALIZATION
        self._fill_tab("VIRTUAL", [
            ("Docker System Prune", "docker system prune -f"),
            ("Docker Image Prune", "docker image prune -a -f"),
            ("Docker Volume Prune", "docker volume prune -f"),
            ("Docker Network Prune", "docker network prune -f"),
            ("Docker Builder Prune", "docker builder prune -f"),
            ("Podman Prune", "podman system prune -f"),
            ("Vagrant Global Prune", "vagrant box prune"),
            ("VirtualBox Log Purge", f"find {home}/VirtualBox\ VMs -name '*.log' -delete"),
            ("KVM Log Cleanup", "sudo rm -rf /var/log/libvirt/qemu/*.log"),
            ("Clean Multipass", "multipass purge"),
        ])

        # Tab: WEB & JS
        self._fill_tab("WEB/JS", [
            ("NPM Global Cache", "npm cache clean --force"),
            ("PNPM Store Prune", "pnpm store prune"),
            ("Yarn Cache Clean", "yarn cache clean"),
            ("Bower Cache Clean", "bower cache clean"),
            ("Clean node_modules", "find . -name 'node_modules' -type d -prune -exec rm -rf '{}' +"),
            ("Purge .next Build", "find . -name '.next' -type d -prune -exec rm -rf '{}' +"),
            ("Purge .nuxt Build", "find . -name '.nuxt' -type d -prune -exec rm -rf '{}' +"),
            ("Cypress Binaries", f"rm -rf {home}/.cache/Cypress"),
            ("Puppeteer Browser", f"rm -rf {home}/.cache/puppeteer"),
            ("Deno Cache Purge", f"rm -rf {home}/.cache/deno"),
        ])

        # Tab: PYTHON & DATA
        self._fill_tab("PYTHON", [
            ("Purge PyCache", "find . -name '__pycache__' -type d -exec rm -rf '{}' +"),
            ("Remove .pyc Files", "find . -name '*.pyc' -delete"),
            ("Pip Cache Clean", "pip cache purge"),
            ("Conda Full Clean", "conda clean -a -y"),
            ("Poetry Cache", f"rm -rf {home}/.cache/pypoetry"),
            ("Jupyter Log Wipe", f"rm -rf {home}/.jupyter/logs/*"),
            ("Pyenv Shims", f"rm -rf {home}/.pyenv/shims/*"),
            ("Wipe .tox Dirs", "find . -name '.tox' -type d -exec rm -rf '{}' +"),
            ("Clean .pytest_cache", "find . -name '.pytest_cache' -type d -exec rm -rf '{}' +"),
            ("Wipe .ipynb_check", "find . -name '.ipynb_checkpoints' -type d -exec rm -rf '{}' +"),
        ])

        # Tab: BUILD SYSTEM
        self._fill_tab("BUILD", [
            ("Cargo Clean All", "cargo clean"),
            ("Go Cache Mod", "go clean -cache -modcache"),
            ("Maven Repo Wipe", f"rm -rf {home}/.m2/repository/*"),
            ("Gradle Cache Wipe", f"rm -rf {home}/.gradle/caches/*"),
            ("C++ .o Cleanup", "find . -name '*.o' -delete"),
            ("C++ .a Cleanup", "find . -name '*.a' -delete"),
            ("Clean CMake Build", "find . -name 'CMakeCache.txt' -delete"),
            ("Wipe build/ dist/", "rm -rf build/ dist/"),
            ("Java .class Purge", "find . -name '*.class' -delete"),
            ("Objective-C Derived", f"rm -rf {home}/Library/Developer/Xcode/DerivedData/*"),
        ])

        # Tab: CLOUD & IDE
        self._fill_tab("CLOUD/IDE", [
            ("AWS CLI Cache", f"rm -rf {home}/.aws/cli/cache/*"),
            ("GCloud Log Purge", f"rm -rf {home}/.config/gcloud/logs/*"),
            ("Azure CLI Telemetry", f"rm -rf {home}/.azure/*.log"),
            ("VSCode Cache Wipe", f"rm -rf {home}/.config/Code/Cache/*"),
            ("VSCode GPU Wipe", f"rm -rf {home}/.config/Code/GPUCache/*"),
            ("IntelliJ Index Wipe", f"find {home}/.cache/JetBrains -name 'index' -type d -exec rm -rf '{{}}' +"),
            ("Sublime Cache", f"rm -rf {home}/.config/sublime-text-3/Cache/*"),
            ("Android Build Cache", f"rm -rf {home}/.android/build-cache"),
            ("Heroku Cache", f"rm -rf {home}/.cache/heroku"),
            ("Vim Swap Cleanup", f"rm -rf {home}/.local/share/vim/swap/*"),
        ])

        # Tab: GIT
        self._fill_tab("GIT", [
            ("Aggressive GC", "git gc --prune=now --aggressive"),
            ("Expire Reflog", "git reflog expire --expire=now --all"),
            ("Git Fsck Full", "git fsck --full --unreachable"),
            ("Prune Remotes", "git remote prune origin"),
            ("Clear Local Logs", "rm -rf .git/logs/"),
            ("Clean Ignored", "git clean -fdX"),
            ("Wipe .git/refs/orig", "rm -rf .git/refs/original/"),
            ("Pack Unpacked", "git pack-refs --all"),
            ("Clean Rebase Temp", "rm -rf .git/rebase-apply .git/rebase-merge"),
            ("Git LFS Prune", "git lfs prune"),
        ])

    def _fill_tab(self, tab_name, tools):
        # Force high visibility white text for all dark-based themes
        is_lite = self.theme.get('bg') == "#F2F2F2"
        text_col = "#000000" if is_lite else "#FFFFFF"
        
        container = ctk.CTkScrollableFrame(self.tabs.tab(tab_name), fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        for name, cmd in tools:
            btn = ctk.CTkButton(container, text=name, height=45,
                               fg_color=self.theme['surface'], text_color=text_col,
                               border_width=2, border_color=self.theme['border'],
                               font=get_font('body'), anchor="w",
                               command=lambda c=cmd, n=name: self._run_tool(c, n))
            btn.pack(fill="x", pady=4, padx=5)

    def _run_tool(self, cmd, name):
        try:
            subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            messagebox.showinfo("Dev Tool", f"Execution complete: {name}")
        except Exception as e:
            messagebox.showerror("Error", f"Execution failed: {str(e)}")
