import os
import time
import psutil

class DeepCleaner:
    def scan_ghost_files(self):
        """Finds deleted files that are still held open by processes."""
        ghosts = []
        try:
            current_user = os.getlogin()
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    # Filter for current user to avoid permission errors
                    if proc.info['username'] != current_user:
                        continue
                        
                    for item in proc.open_files():
                        if item.path.endswith(' (deleted)'):
                            path = item.path.replace(' (deleted)', '')
                            ghosts.append({
                                "name": f"{proc.info['name']} (PID: {proc.info['pid']})",
                                "path": path, # Only for display, deleting this does nothing
                                "size": 0,    # Hard to get size of deleted file
                                "type": "Ghost File",
                                "pid": proc.info['pid'] # Store PID to kill later
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except: pass
        return ghosts

    def scan_broken_links(self, start_path):
        broken = []
        # Walk recursively
        for root, dirs, files in os.walk(start_path):
            for f in files:
                full_path = os.path.join(root, f)
                if os.path.islink(full_path):
                    try:
                        target = os.readlink(full_path)
                        # Resolve relative symlinks
                        if not os.path.isabs(target):
                            target = os.path.join(os.path.dirname(full_path), target)
                        
                        if not os.path.exists(target):
                            broken.append({
                                "name": f,
                                "path": full_path,
                                "size": 0,
                                "type": "Broken Link"
                            })
                    except: pass
        return broken

    def scan_old_logs(self, days=14):
        old_logs = []
        now = time.time()
        limit = days * 86400
        
        # Scan user cache/log areas
        scan_dirs = [os.path.expanduser("~/.cache"), os.path.expanduser("~/.local/share")]
        
        for d in scan_dirs:
            if not os.path.exists(d): continue
            for root, _, files in os.walk(d):
                for f in files:
                    # Match log patterns
                    if f.endswith(('.log', '.log.gz', '.old', '.1', '.journal')):
                        p = os.path.join(root, f)
                        try:
                            if (now - os.path.getmtime(p)) > limit:
                                old_logs.append({
                                    "name": f,
                                    "path": p,
                                    "size": os.path.getsize(p),
                                    "type": f"Old Log (>{days}d)"
                                })
                        except: pass
        return old_logs
