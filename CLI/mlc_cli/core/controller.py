import threading
import psutil
import os
import shutil
import time
import subprocess
from ..cleaners.system_cleaner import SystemOptimizer, StartupManager
from ..cleaners.package_manager import PackageManager
from ..cleaners.health_manager import HealthManager
from ..cleaners.engine import CleaningEngine
from ..tools.analyzers import FileAnalyzer
from ..tools.backup import BackupManager
from .auth import get_password

class CLIController:
    def __init__(self):
        self.engine = CleaningEngine()
        self.optimizer = SystemOptimizer(None, self.get_auth)
        self.startup = StartupManager()
        self.packages = PackageManager()
        self.health = HealthManager()
        self.analyzer = FileAnalyzer()
        self.backup_mgr = BackupManager()
        self.cached_password = None

    def get_auth(self):
        """Internal callback to get password for sudo operations."""
        if self.cached_password:
            return self.cached_password
        
        pw = get_password()
        if pw:
            self.cached_password = pw
        return pw

    def get_sys_info(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_percent": psutil.virtual_memory().percent,
            "ram_total": psutil.virtual_memory().total,
            "ram_used": psutil.virtual_memory().used,
            "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else (0,0,0)
        }

    def get_drives(self):
        drives = []
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
        return drives

    def get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'user': info['username'] or "N/A",
                    'status': info['status'],
                    'cpu': info['cpu_percent'],
                    'ram': info['memory_info'].rss,
                    'uptime': time.time() - info['create_time']
                })
            except: continue
        return sorted(processes, key=lambda x: x['cpu'], reverse=True)

    def kill_process(self, pid):
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True, "Process terminated."
        except Exception as e:
            return False, str(e)

    def create_snapshot(self, src, dest):
        return self.backup_mgr.create_snapshot(src, dest)

    def restore_snapshot(self, src, dest):
        return self.backup_mgr.restore_snapshot(src, dest)

    def compare_snapshot(self, src, original):
        return self.backup_mgr.compare_snapshot(src, original)
