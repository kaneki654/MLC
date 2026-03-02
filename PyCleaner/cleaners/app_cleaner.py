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

        # 4. VS Code Cache
        vscode_paths = [
            os.path.join(home, ".config", "Code", "Cache"),
            os.path.join(home, ".config", "Code", "CachedData"),
            os.path.join(home, ".config", "Code", "Service Worker", "CacheStorage")
        ]
        for path in vscode_paths:
            if os.path.exists(path):
                results.append({"name": f"VS Code: {os.path.basename(path)}", "path": path, "size": self._get_size(path), "type": "App Cache"})

        # 5. Slack Cache
        slack_paths = [
            os.path.join(home, ".config", "Slack", "Cache"),
            os.path.join(home, ".config", "Slack", "Service Worker", "CacheStorage")
        ]
        for path in slack_paths:
            if os.path.exists(path):
                results.append({"name": f"Slack: {os.path.basename(path)}", "path": path, "size": self._get_size(path), "type": "App Cache"})

        # 6. Zoom Cache
        # Check ~/.zoom/data and ~/.config/zoomus
        zoom_paths = [
            os.path.join(home, ".zoom", "data"),
            os.path.join(home, ".config", "zoomus")
        ]
        for path in zoom_paths:
            if os.path.exists(path):
                results.append({"name": f"Zoom: {os.path.basename(path)}", "path": path, "size": self._get_size(path), "type": "App Cache"})

        # 7. Thumbnails
        thumbnails = os.path.join(home, ".cache", "thumbnails")
        if os.path.exists(thumbnails):
            results.append({"name": "Thumbnails Cache", "path": thumbnails, "size": self._get_size(thumbnails), "type": "System Cache"})

        # 8. Yarn/NPM Cache
        npm_cache = os.path.join(home, ".npm", "_cacache")
        if os.path.exists(npm_cache):
            results.append({"name": "NPM Cache", "path": npm_cache, "size": self._get_size(npm_cache), "type": "Dev Cache"})
            
        yarn_cache = os.path.join(home, ".cache", "yarn")
        if os.path.exists(yarn_cache):
            results.append({"name": "Yarn Cache", "path": yarn_cache, "size": self._get_size(yarn_cache), "type": "Dev Cache"})

        # 9. Pip Cache
        pip_cache = os.path.join(home, ".cache", "pip")
        if os.path.exists(pip_cache):
            results.append({"name": "Pip Cache", "path": pip_cache, "size": self._get_size(pip_cache), "type": "Dev Cache"})

        # 10. Go Cache
        go_cache = os.path.join(home, ".cache", "go-build")
        if os.path.exists(go_cache):
            results.append({"name": "Go Build Cache", "path": go_cache, "size": self._get_size(go_cache), "type": "Dev Cache"})

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
