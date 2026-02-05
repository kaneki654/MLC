import os
import shutil

class BrowserCleaner:
    def __init__(self):
        self.browsers = {
            'Chrome': os.path.expanduser('~/.config/google-chrome'),
            'Chromium': os.path.expanduser('~/.config/chromium'),
            'Firefox': os.path.expanduser('~/.mozilla/firefox')
        }

    def scan(self):
        found = []
        for name, path in self.browsers.items():
            if not os.path.exists(path):
                continue
                
            # Chrome/Chromium Cache
            if 'Chrome' in name or 'Chromium' in name:
                cache_path = os.path.join(path, 'Default', 'Cache')
                if os.path.exists(cache_path):
                    size = self._get_size(cache_path)
                    found.append({"name": f"{name} Cache", "path": cache_path, "size": size, "type": "Browser"})
                
                code_cache = os.path.join(path, 'Default', 'Code Cache')
                if os.path.exists(code_cache):
                    size = self._get_size(code_cache)
                    found.append({"name": f"{name} Code Cache", "path": code_cache, "size": size, "type": "Browser"})

            # Firefox Cache (Often in ~/.cache/mozilla/firefox, not .mozilla)
            elif name == 'Firefox':
                # Check ~/.cache version for actual cache
                cache_root = os.path.expanduser('~/.cache/mozilla/firefox')
                if os.path.exists(cache_root):
                    for profile in os.listdir(cache_root):
                        p_path = os.path.join(cache_root, profile)
                        if os.path.isdir(p_path):
                            size = self._get_size(p_path)
                            found.append({"name": f"Firefox Cache ({profile[:8]})", "path": p_path, "size": size, "type": "Browser"})

        return found

    def _get_size(self, path):
        total = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                try: total += os.path.getsize(os.path.join(dirpath, f))
                except: pass
        return total
