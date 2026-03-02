import os
import glob
import shutil
import subprocess
import time
from cleaners.browser_cleaner import BrowserCleaner
from cleaners.app_cleaner import AppCleaner

class CleaningEngine:
    def __init__(self):
        self.targets = []
        self._load_definitions()
        self.browser_cleaner = BrowserCleaner()
        self.app_cleaner = AppCleaner()
        self.auth_callback = None
        self.password = None # Cache password for session

    def set_auth(self, callback):
        self.auth_callback = callback

    def _load_definitions(self):
        home = os.path.expanduser("~")
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
        
        locales = ['af', 'am', 'ar', 'as', 'ast', 'az', 'be', 'bg', 'bn', 'br', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en_AU', 'en_GB', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 'fr', 'ga', 'gd', 'gl', 'gu', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'ja', 'ka', 'kk', 'km', 'kn', 'ko', 'ku', 'ky', 'lt', 'lv', 'mk', 'ml', 'mn', 'mr', 'ms', 'nb', 'ne', 'nl', 'nn', 'oc', 'or', 'pa', 'pl', 'ps', 'pt', 'ro', 'ru', 'rw', 'si', 'sk', 'sl', 'sq', 'sr', 'sv', 'ta', 'te', 'th', 'tr', 'ug', 'uk', 'uz', 'vi', 'wa', 'zh_CN', 'zh_TW']
        for loc in locales:
            sys_targets.append((f"Locale: {loc.upper()}", f"/usr/share/locale/{loc}/*", f"Localization files for {loc}."))

        scan_dirs = ["Downloads", "Videos", "Documents", "Desktop", "Music", "Pictures", ".local/share"]
        extensions = [".iso", ".zip", ".tar.gz", ".mp4", ".mkv", ".mov", ".bak", ".old", ".tmp", ".msi", ".dmg", ".qcow2", ".vmdk", ".raw", ".ova"]
        
        for d in scan_dirs:
            dir_path = os.path.join(home, d)
            if os.path.exists(dir_path):
                for ext in extensions:
                    self.add_target("LARGE DATA", f"{d}: {ext.upper()} Discovery", f"{dir_path}/**/*{ext}", f"Large {ext} files in {d}.")

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
                        results.append({"name": target['name'], "path": target['pattern'], "size": 0, "type": target['category'], "description": target['description'], "is_cmd": True})
                else:
                    found_files = glob.iglob(target['pattern'], recursive=True, include_hidden=True)
                    for f in found_files:
                        if f in seen_paths: continue
                        if os.path.isfile(f) or os.path.islink(f):
                            try:
                                sz = os.path.getsize(f)
                                if sz > 0:
                                    if target['category'] == "LARGE DATA" and sz < 50 * 1024 * 1024: continue
                                    results.append({"name": target['name'], "path": f, "size": sz, "type": target['category'], "description": target['description'], "is_cmd": False})
                                    seen_paths.add(f)
                            except: pass
            except: pass

        browser_results = self.browser_cleaner.scan()
        for res in browser_results:
            if res['path'] not in seen_paths:
                res['description'] = "Browser cache/data"
                res['is_cmd'] = False
                results.append(res)
                seen_paths.add(res['path'])

        app_results = self.app_cleaner.scan_apps()
        for res in app_results:
            if res['path'] not in seen_paths:
                res['description'] = "Application cache/data"
                res['is_cmd'] = False
                results.append(res)
                seen_paths.add(res['path'])
        return results

    def _privileged_rm(self, path):
        """Uses sudo -S to remove files if permission denied."""
        if not self.auth_callback and os.geteuid() != 0: return False
        
        if os.geteuid() != 0:
            if not self.password:
                self.password = self.auth_callback()
            if not self.password: return False
            
            try:
                # -S reads password from stdin
                cmd = f"sudo -S rm -rf '{path}'"
                proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                proc.communicate(input=f"{self.password}\n")
                return proc.returncode == 0
            except: return False
        else:
            # Already root
            try:
                if os.path.isfile(path) or os.path.islink(path): os.remove(path)
                elif os.path.isdir(path): shutil.rmtree(path)
                return True
            except: return False

    def clean(self, items, mode='delete', callback_done=None):
        count = 0
        reclaimed = 0
        trash_path = os.path.expanduser("~/.local/share/Trash/files")
        if mode == 'trash': os.makedirs(trash_path, exist_ok=True)

        for item in items:
            try:
                p = item['path']
                size = item.get('size', 0)
                if item.get('is_cmd'):
                    cmd = p.split(":", 1)[1]
                    if os.geteuid() != 0:
                        if not self.password: self.password = self.auth_callback()
                        if self.password:
                            subprocess.run(f"echo '{self.password}' | sudo -S {cmd}", shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        subprocess.run(cmd, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    if os.path.exists(p):
                        if mode == 'shred': subprocess.run(["shred", "-u", "-z", p], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif mode == 'trash':
                            try:
                                dest = os.path.join(trash_path, os.path.basename(p))
                                if os.path.exists(dest):
                                    base, ext = os.path.splitext(dest)
                                    dest = f"{base}_{int(time.time())}{ext}"
                                shutil.move(p, dest)
                            except: os.remove(p)
                        else:
                            # Try standard delete, fallback to privileged if permission denied
                            try:
                                if os.path.isfile(p) or os.path.islink(p): os.remove(p)
                                elif os.path.isdir(p): shutil.rmtree(p)
                            except PermissionError:
                                self._privileged_rm(p)
                        count += 1
                        reclaimed += size
            except: pass
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
            history.append({"timestamp": time.time(), "items": count, "reclaimed": bytes_freed})
            with open(history_path, "w") as f: json.dump(history[-50:], f)
        except: pass
