import os
import shutil

class BrowserCleaner:
    def __init__(self):
        # Chromium-based browsers (Base Config Path)
        self.chromium_browsers = {
            'Google Chrome': os.path.expanduser('~/.config/google-chrome'),
            'Chromium': os.path.expanduser('~/.config/chromium'),
            'Brave': os.path.expanduser('~/.config/BraveSoftware/Brave-Browser'),
            'Vivaldi': os.path.expanduser('~/.config/vivaldi'),
            'Microsoft Edge': os.path.expanduser('~/.config/microsoft-edge'),
            'Opera': os.path.expanduser('~/.config/opera'),
        }
        
        # Firefox-based browsers (Config Path, Cache Path)
        self.firefox_browsers = {
            'Firefox': {
                'config': os.path.expanduser('~/.mozilla/firefox'),
                'cache': os.path.expanduser('~/.cache/mozilla/firefox')
            },
            'LibreWolf': {
                'config': os.path.expanduser('~/.librewolf'),
                'cache': os.path.expanduser('~/.cache/librewolf')
            }
        }

    def scan(self):
        found = []
        
        # 1. Scan Chromium-based browsers
        for name, base_path in self.chromium_browsers.items():
            if not os.path.exists(base_path):
                continue

            # Standard Chromium cache targets
            targets = [
                ('Cache', os.path.join(base_path, 'Default', 'Cache')),
                ('Code Cache', os.path.join(base_path, 'Default', 'Code Cache')),
                ('GPUCache', os.path.join(base_path, 'Default', 'GPUCache')),
                ('Service Worker Cache', os.path.join(base_path, 'Default', 'Service Worker', 'CacheStorage')),
            ]
            
            for label, path in targets:
                if os.path.exists(path):
                    size = self._get_size(path)
                    if size > 0:
                        found.append({
                            "name": f"{name} {label}",
                            "path": path,
                            "size": size,
                            "type": "Browser Cache"
                        })

        # 2. Scan Firefox-based browsers
        for name, paths in self.firefox_browsers.items():
            # A. Scan ~/.cache location (Primary Cache)
            cache_root = paths['cache']
            if os.path.exists(cache_root):
                try:
                    for profile in os.listdir(cache_root):
                        p_path = os.path.join(cache_root, profile)
                        if os.path.isdir(p_path):
                            size = self._get_size(p_path)
                            if size > 0:
                                found.append({
                                    "name": f"{name} Cache ({profile})",
                                    "path": p_path,
                                    "size": size,
                                    "type": "Browser Cache"
                                })
                except OSError:
                    pass

            # B. Scan ~/.mozilla location (Secondary Caches like startupCache)
            config_root = paths['config']
            if os.path.exists(config_root):
                try:
                    for item in os.listdir(config_root):
                        profile_path = os.path.join(config_root, item)
                        if os.path.isdir(profile_path):
                            # Look for specific cache directories inside the profile folder
                            internal_targets = ['startupCache', 'shader-cache', 'jumpListCache']
                            for target in internal_targets:
                                target_path = os.path.join(profile_path, target)
                                if os.path.exists(target_path):
                                    size = self._get_size(target_path)
                                    if size > 0:
                                        found.append({
                                            "name": f"{name} {target} ({item})",
                                            "path": target_path,
                                            "size": size,
                                            "type": "Browser Cache"
                                        })
                except OSError:
                    pass

        return found

    def _get_size(self, path):
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    try: 
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp):
                            total += os.path.getsize(fp)
                    except: pass
        except: pass
        return total
