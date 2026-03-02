import threading
import psutil
import os
import shutil
import time
import subprocess
from cleaners.system_cleaner import SystemOptimizer, StartupManager
from cleaners.package_manager import PackageManager
from cleaners.health_manager import HealthManager
from cleaners.engine import CleaningEngine
from tools.analyzers import FileAnalyzer
from tools.backup import BackupManager

class ScannerWorker:
    def __init__(self, auth_callback=None):
        self.stop_event = threading.Event()
        self.auth_callback = auth_callback
        self.is_root = (os.geteuid() == 0)
        
        self.engine = CleaningEngine()
        self.engine.set_auth(auth_callback)
        
        self.optimizer = SystemOptimizer(None, auth_callback)
        self.startup = StartupManager()
        self.packages = PackageManager()
        self.health = HealthManager()
        self.analyzer = FileAnalyzer()
        self.backup_mgr = BackupManager()
        self.whitelist = set()

    def add_to_whitelist(self, path):
        self.whitelist.add(path)

    def get_drives(self):
        drives = []
        try:
            for p in psutil.disk_partitions():
                if 'loop' in p.device: continue 
                try:
                    u = psutil.disk_usage(p.mountpoint)
                    drives.append({
                        "device": p.device, 
                        "mountpoint": p.mountpoint, 
                        "percent": u.percent, 
                        "free": u.free, 
                        "total": u.total,
                        "fstype": p.fstype
                    })
                except: pass
        except: pass
        return drives

    def get_sys_info(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_percent": psutil.virtual_memory().percent,
            "ram_total": psutil.virtual_memory().total,
            "ram_used": psutil.virtual_memory().used,
            "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else (0,0,0)
        }

    def boost_ram(self):
        return self.optimizer.drop_caches()
    
    def optimize_swap(self):
        return self.optimizer.optimize_swap()

    def get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_info', 'create_time', 'cmdline']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'user': info['username'],
                    'status': info['status'],
                    'cpu': info['cpu_percent'],
                    'ram': info['memory_info'].rss,
                    'uptime': time.time() - info['create_time'],
                    'cmd': " ".join(info['cmdline']) if info['cmdline'] else "N/A"
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes

    def kill_process(self, pid, force=False):
        try:
            proc = psutil.Process(pid)
            if force: proc.kill()
            else: proc.terminate()
            return True, "Process terminated"
        except Exception as e:
            return False, str(e)

    def scan_all_junk(self, user_path, callback):
        def _run():
            results = self.engine.scan()
            callback(results)
        threading.Thread(target=_run, daemon=True).start()

    def delete_items(self, items, callback):
        def _run():
            count = self.engine.clean(items)
            callback(count)
        threading.Thread(target=_run, daemon=True).start()

    def elevate(self):
        """Restarts the app as root using pkexec with environment preservation."""
        import sys
        try:
            # We need to pass the DISPLAY and XAUTHORITY to allow root to open a GUI window
            env_vars = []
            if "DISPLAY" in os.environ:
                env_vars.append(f"DISPLAY={os.environ['DISPLAY']}")
            if "XAUTHORITY" in os.environ:
                env_vars.append(f"XAUTHORITY={os.environ['XAUTHORITY']}")
            else:
                # Fallback for XAUTHORITY if not in env
                xauth = os.path.expanduser("~/.Xauthority")
                if os.path.exists(xauth):
                    env_vars.append(f"XAUTHORITY={xauth}")
            
            # The command to run as root
            python_cmd = [sys.executable] + sys.argv
            cmd = ["pkexec", "env"] + env_vars + python_cmd
            
            subprocess.Popen(cmd)
            sys.exit(0)
        except Exception as e:
            return False, str(e)

    def create_snapshot(self, src, dest):
        return self.backup_mgr.create_snapshot(src, dest)

    def restore_snapshot(self, src, dest):
        return self.backup_mgr.restore_snapshot(src, dest)

    def compare_snapshot(self, src, original):
        return self.backup_mgr.compare_snapshot(src, original)

    def scan_large_files(self, path, callback):
        threading.Thread(target=lambda: callback(self.analyzer.find_large_files(path)), daemon=True).start()

    def scan_duplicates(self, path, callback):
        threading.Thread(target=lambda: callback(self.analyzer.find_duplicates(path)), daemon=True).start()

    def scan_empty_folders(self, path, callback):
        def _scan():
            empty = []
            for root, dirs, files in os.walk(path, topdown=False):
                for name in dirs:
                    try:
                        p = os.path.join(root, name)
                        if not os.listdir(p):
                            empty.append({"path": p, "name": name, "size": 0, "type": "Empty Folder"})
                    except: pass
            callback(empty)
        threading.Thread(target=_scan, daemon=True).start()

    def shred_item(self, path):
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                with open(path, "wb") as f: f.write(b'\0' * size)
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True
        except: return False

    def prune_docker(self):
        try:
            subprocess.run(["docker", "system", "prune", "-f"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except: return False
