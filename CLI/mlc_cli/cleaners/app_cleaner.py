import os

class AppCleaner:
    def scan_apps(self):
        results = []
        home = os.path.expanduser("~")
        
        # 1. Flatpak Cache
        flatpak = os.path.join(home, ".var", "app")
        if os.path.exists(flatpak):
            # We can't delete the whole folder, but we can look for 'cache' inside each app
            try:
                for app in os.listdir(flatpak):
                    cache_path = os.path.join(flatpak, app, "cache")
                    if os.path.exists(cache_path):
                        size = self._get_size(cache_path)
                        if size > 0:
                            results.append({"name": f"Flatpak: {app}", "path": cache_path, "size": size, "type": "App Cache"})
            except: pass

        # 2. Discord Cache
        discord = os.path.join(home, ".config", "discord", "Cache")
        if os.path.exists(discord):
            results.append({"name": "Discord Cache", "path": discord, "size": self._get_size(discord), "type": "App Cache"})
            
        # 3. Spotify Cache
        spotify = os.path.join(home, ".cache", "spotify")
        if os.path.exists(spotify):
            results.append({"name": "Spotify Cache", "path": spotify, "size": self._get_size(spotify), "type": "App Cache"})

        return results

    def clean_snap_cache(self):
        """Removes disabled snaps (requires sudo usually, or just cache)."""
        # /var/lib/snapd/cache is root only.
        # We can clean user-local snap data
        p = os.path.expanduser("~/snap/common/cache")
        if os.path.exists(p):
            return {"name": "User Snap Cache", "path": p, "size": self._get_size(p), "type": "App Cache"}
        return None

    def _get_size(self, path):
        total = 0
        try:
            for root, dirs, files in os.walk(path):
                for f in files:
                    try: total += os.path.getsize(os.path.join(root, f))
                    except: pass
        except: pass
        return total
