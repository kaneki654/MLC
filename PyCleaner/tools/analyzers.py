import os
import hashlib

class FileAnalyzer:
    def find_large_files(self, path, limit=100, min_size_mb=50):
        large_files = []
        min_bytes = min_size_mb * 1024 * 1024
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_root = os.path.dirname(script_dir)
        exclude_dirs = {app_root, "/proc", "/sys", "/dev", "/run", "/var/run"}

        for root, dirs, files in os.walk(path, topdown=True):
            abs_root = os.path.abspath(root)
            if any(abs_root.startswith(ex) for ex in exclude_dirs):
                dirs[:] = [] 
                continue

            for f in files:
                try:
                    full_path = os.path.join(root, f)
                    stat = os.lstat(full_path)
                    size = stat.st_size
                    if size > min_bytes:
                        large_files.append({"path": full_path, "name": f, "size": size})
                except (PermissionError, OSError):
                    continue
        
        large_files.sort(key=lambda x: x['size'], reverse=True)
        return large_files[:limit]

    def find_duplicates(self, path, callback_progress=None):
        size_map = {}
        total_files = 0
        
        # 1. Group by size first (fast)
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    p = os.path.join(root, f)
                    if os.path.islink(p): continue
                    s = os.path.getsize(p)
                    if s < 4096: continue # Skip tiny files (< 4KB)
                    if s not in size_map: size_map[s] = []
                    size_map[s].append(p)
                    total_files += 1
                except: pass
        
        # 2. Hash files with same size (Optimized for AMD A4)
        duplicates = []
        processed = 0
        for size, paths in size_map.items():
            if len(paths) < 2: 
                processed += len(paths)
                continue
            
            hashes = {}
            for p in paths:
                processed += 1
                if callback_progress: callback_progress(processed / total_files, f"Hashing: {os.path.basename(p)}")
                try:
                    # Fast hash first (first 4KB + last 4KB)
                    h = self._get_fast_hash(p, size)
                    if h not in hashes: hashes[h] = []
                    hashes[h].append(p)
                except: pass
            
            for h, p_list in hashes.items():
                if len(p_list) > 1:
                    # For those that matched fast hash, do a full hash to be 100% sure
                    real_hashes = {}
                    for p in p_list:
                        try:
                            rh = self._get_hash(p)
                            if rh not in real_hashes: real_hashes[rh] = []
                            real_hashes[rh].append(p)
                        except: pass
                    
                    for rh, rp_list in real_hashes.items():
                        if len(rp_list) > 1:
                            duplicates.append({"hash": rh, "size": size, "paths": rp_list})
                    
        return duplicates

    def _get_fast_hash(self, path, size):
        """Hashes first and last 4KB of file for quick comparison."""
        hasher = hashlib.md5()
        with open(path, 'rb') as f:
            # First 4KB
            hasher.update(f.read(4096))
            if size > 8192:
                # Last 4KB
                f.seek(-4096, 2)
                hasher.update(f.read(4096))
        return hasher.hexdigest()

    def _get_hash(self, path, chunk_size=65536):
        """Full MD5 hash with larger chunk size for better throughput on old CPUs."""
        hasher = hashlib.md5()
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
