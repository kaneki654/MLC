import os
import hashlib

class FileAnalyzer:
    def find_large_files(self, path, limit=100, min_size_mb=50):
        large_files = []
        min_bytes = min_size_mb * 1024 * 1024
        
        # Get the absolute path of the current script to exclude it
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root = os.path.dirname(script_dir)

        # Virtual filesystems and app root to exclude
        exclude_dirs = {app_root, "/proc", "/sys", "/dev", "/run", "/var/run"}

        for root, dirs, files in os.walk(path, topdown=True):
            # Resolve root to absolute path
            abs_root = os.path.abspath(root)
            
            # Efficiently skip excluded directories
            if any(abs_root.startswith(ex) for ex in exclude_dirs):
                dirs[:] = [] 
                continue

            for f in files:
                try:
                    full_path = os.path.join(root, f)
                    # Use lstat to avoid following broken symlinks that might crash
                    stat = os.lstat(full_path)
                    size = stat.st_size
                    if size > min_bytes:
                        large_files.append({"path": full_path, "name": f, "size": size})
                except (PermissionError, OSError):
                    continue
        
        # Sort by size descending
        large_files.sort(key=lambda x: x['size'], reverse=True)
        return large_files[:limit]

    def find_duplicates(self, path):
        # 1. Group by size first (fast)
        size_map = {}
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    p = os.path.join(root, f)
                    s = os.path.getsize(p)
                    if s < 1024: continue # Skip tiny files
                    if s not in size_map: size_map[s] = []
                    size_map[s].append(p)
                except: pass
        
        # 2. Hash files with same size
        duplicates = []
        for size, paths in size_map.items():
            if len(paths) < 2: continue
            
            hashes = {}
            for p in paths:
                try:
                    h = self._get_hash(p)
                    if h not in hashes: hashes[h] = []
                    hashes[h].append(p)
                except: pass
            
            for h, p_list in hashes.items():
                if len(p_list) > 1:
                    duplicates.append({"hash": h, "size": size, "paths": p_list})
                    
        return duplicates

    def _get_hash(self, path, chunk_size=8192):
        # Read only first block for speed optimization initially? 
        # No, full hash for safety.
        hasher = hashlib.md5()
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
