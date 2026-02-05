import os
import glob
import shutil
import subprocess
import time

class CleaningEngine:
    def __init__(self):
        self.targets = []
        self._load_definitions()

    def _load_definitions(self):
        home = os.path.expanduser("~")
        
        # --- SYSTEM (150+ Targets) ---
        sys_targets = [
            ("Old Packages", "/var/cache/apt/archives/*.deb", "Cached DEB packages from apt-get."),
            ("Partial Downloads", "/var/cache/apt/archives/partial/*", "Incomplete package downloads."),
            ("Journal Logs", "command:journalctl --vacuum-time=1d", "Systemd logs older than 1 day."),
            ("Thumbnails (Normal)", f"{home}/.cache/thumbnails/normal/*", "Cached image thumbnails."),
            ("Thumbnails (Large)", f"{home}/.cache/thumbnails/large/*", "High-res thumbnails."),
            ("Crash Reports", "/var/crash/*", "System crash dump files."),
            ("Core Dumps", "/var/lib/systemd/coredump/*", "Process memory dumps."),
            ("Temp Files", "/tmp/*", "Temporary system files."),
            ("User Cache", f"{home}/.cache/*", "General user application cache."),
            ("Systemd Logs", "/var/log/journal/*", "Binary system logs."),
            ("Apt Old Lists", "/var/lib/apt/lists/*", "Package lists from update."),
            ("Man Database Cache", "/var/cache/man/*", "Manual page index cache."),
            ("Fontconfig Cache", f"{home}/.cache/fontconfig/*", "Font render cache."),
            ("Icon Cache", f"{home}/.cache/icon-cache.kcache", "Icon theme cache."),
            ("Gstreamer Registry", f"{home}/.cache/gstreamer-1.0/*", "Media framework registry."),
            ("PulseAudio State", f"{home}/.config/pulse/*", "Audio server state."),
            ("Flatpak Metadata", f"{home}/.local/share/flatpak/.metadata/*", "Flatpak app metadata."),
            ("X11 Error Logs", f"{home}/.xsession-errors*", "Display server error logs."),
        ]
        
        # Massive Locale Cleanup (approx 100 targets)
        locales = ['af', 'am', 'ar', 'as', 'ast', 'az', 'be', 'bg', 'bn', 'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en_AU', 'en_GB', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'gd', 'gl', 'gu', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'lt', 'lv', 'mk', 'ml', 'mn', 'mr', 'ms', 'nb', 'ne', 'nl', 'nn', 'oc', 'or', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'rw', 'si', 'sk', 'sl', 'sq', 'sr', 'sv', 'ta', 'te', 'th', 'tr', 'ug', 'uk', 'uz', 'vi', 'wa', 'zh_CN', 'zh_TW']
        for loc in locales:
            sys_targets.append((f"Locale: {loc.upper()}", f"/usr/share/locale/{loc}/*", f"Localization files for {loc}."))

        # --- LARGE BLOB DISCOVERY (The 1TB+ Goal) ---
        scan_dirs = ["Downloads", "Videos", "Documents", "Desktop", "Music", "Pictures", ".local/share"]
        extensions = [".iso", ".zip", ".tar.gz", ".mp4", ".mkv", ".mov", ".bak", ".old", ".tmp", ".msi", ".dmg", ".qcow2", ".vmdk", ".raw", ".ova"]
        
        for d in scan_dirs:
            dir_path = os.path.join(home, d)
            if os.path.exists(dir_path):
                for ext in extensions:
                    self.add_target("LARGE DATA", f"{d}: {ext.upper()} Discovery", f"{dir_path}/**/*{ext}", f"Large {ext} files in {d}.")

        # --- BROWSERS (80+ Targets) ---
        browsers = {
            "Chrome": [f"{home}/.config/google-chrome", f"{home}/.cache/google-chrome"],
            "Firefox": [f"{home}/.mozilla/firefox", f"{home}/.cache/mozilla/firefox"],
            "Brave": [f"{home}/.config/BraveSoftware/Brave-Browser", f"{home}/.cache/BraveSoftware/Brave-Browser"],
            "Edge": [f"{home}/.config/microsoft-edge", f"{home}/.cache/microsoft-edge"],
            "Opera": [f"{home}/.config/opera", f"{home}/.cache/opera"],
            "Vivaldi": [f"{home}/.config/vivaldi", f"{home}/.cache/vivaldi"],
            "Librewolf": [f"{home}/.librewolf", f"{home}/.cache/librewolf"],
            "Chromium": [f"{home}/.config/chromium", f"{home}/.cache/chromium"],
            "Sidekick": [f"{home}/.config/sidekick"],
            "Waterfox": [f"{home}/.waterfox"],
            "Pale Moon": [f"{home}/.moonchild productions"]
        }
        
        browser_subs = ["Cache", "Code Cache", "GPUCache", "Media Cache", "Service Worker", "databases", "IndexedDB", "Local Storage", "Favicons"]
        for name, paths in browsers.items():
            for p in paths:
                for sub in browser_subs:
                    self.add_target("BROWSERS", f"{name}: {sub}", f"{p}/**/{sub}/*", f"Browser {sub.lower()} data.")

        # --- APPS (70+ Targets) ---
        apps = ["Discord", "Slack", "Teams", "VSCode", "Spotify", "Steam", "Wine", "Telegram", "Zoom", "VLC", "GIMP", "OBS", "Skype", "Signal", "Blender", "Inkscape"]
        for app in apps:
            app_lower = app.lower()
            self.add_target("APPS", f"{app}: Cache", f"{home}/.config/{app_lower}/Cache/*", "Application cache.")
            self.add_target("APPS", f"{app}: GPU Cache", f"{home}/.config/{app_lower}/GPUCache/*", "GPU render cache.")
            self.add_target("APPS", f"{app}: Logs", f"{home}/.config/{app_lower}/logs/*", "Application logs.")
            self.add_target("APPS", f"{app}: Temp", f"{home}/.config/{app_lower}/tmp/*", "Temporary files.")

        # Special Steam Shader Cache
        self.add_target("APPS", "Steam: Shader Cache", f"{home}/.steam/steam/steamapps/shadercache/*", "Compiled shader cache.")

        for name, pat, desc in sys_targets: self.add_target("SYSTEM", name, pat, desc)

    def add_target(self, category, name, pattern, description="", risk="Safe"):
        self.targets.append({
            "category": category,
            "name": name,
            "pattern": pattern,
            "description": description,
            "risk": risk,
            "enabled": True
        })

    def scan(self, callback_progress=None):
        results = []
        seen_paths = set()
        total = len(self.targets)
        
        for i, target in enumerate(self.targets):
            if not target['enabled']: continue
            if callback_progress: callback_progress(i / total, target['name'])
            
            try:
                if target['pattern'].startswith("command:"):
                    cmd = target['pattern'].split(":", 1)[1].split()[0]
                    if shutil.which(cmd):
                        results.append({
                            "name": target['name'], 
                            "path": target['pattern'], 
                            "size": 0, 
                            "type": target['category'], 
                            "description": target['description'],
                            "is_cmd": True
                        })
                else:
                    # Recursive glob for deep discovery, including hidden files
                    found_files = glob.iglob(target['pattern'], recursive=True, include_hidden=True)
                    for f in found_files:
                        if f in seen_paths: continue
                        if os.path.isfile(f) or os.path.islink(f):
                            try:
                                sz = os.path.getsize(f)
                                if sz > 0:
                                    # Filter Large Data to > 50MB to avoid clutter
                                    if target['category'] == "LARGE DATA" and sz < 50 * 1024 * 1024:
                                        continue
                                    results.append({
                                        "name": target['name'], 
                                        "path": f, 
                                        "size": sz, 
                                        "type": target['category'], 
                                        "description": target['description'],
                                        "is_cmd": False
                                    })
                                    seen_paths.add(f)
                            except: pass
            except: pass
        return results

    def clean(self, items, mode='delete', callback_done=None):
        count = 0
        reclaimed = 0
        trash_path = os.path.expanduser("~/.local/share/Trash/files")
        
        if mode == 'trash':
            os.makedirs(trash_path, exist_ok=True)

        for item in items:
            try:
                p = item['path']
                size = item.get('size', 0)
                if item.get('is_cmd'):
                    # Trash/Shred doesn't apply to commands, just execute
                    cmd = p.split(":", 1)[1]
                    subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    if os.path.exists(p):
                        if mode == 'shred': # Secure erase
                            subprocess.run(["shred", "-u", "-z", p], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif mode == 'trash': # Move to Trash
                            try:
                                dest = os.path.join(trash_path, os.path.basename(p))
                                if os.path.exists(dest): # Avoid overwrite
                                    base, ext = os.path.splitext(dest)
                                    dest = f"{base}_{int(time.time())}{ext}"
                                shutil.move(p, dest)
                            except: # Fallback if move fails (e.g. diff filesystem)
                                os.remove(p)
                        else: # Standard delete
                            if os.path.isfile(p) or os.path.islink(p): os.remove(p)
                            elif os.path.isdir(p): shutil.rmtree(p)
                        count += 1
                        reclaimed += size
            except: pass
        
        # Log session
        self._log_history(count, reclaimed)
        
        if callback_done: callback_done(count)
        return count

    def _log_history(self, count, bytes_freed):
        import json
        history_path = os.path.expanduser("~/.mlcleaner_history.json")
        try:
            history = []
            if os.path.exists(history_path):
                with open(history_path, "r") as f: history = json.load(f)
            
            history.append({
                "timestamp": time.time(),
                "items": count,
                "reclaimed": bytes_freed
            })
            
            with open(history_path, "w") as f: json.dump(history[-50:], f) # Keep last 50
        except: pass
