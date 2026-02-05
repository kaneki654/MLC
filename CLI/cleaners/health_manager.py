import os
import subprocess
import stat

class HealthManager:
    def get_disk_health(self):
        """Attempts to read SMART data via smartctl."""
        health_data = []
        try:
            # List drives
            drives = subprocess.check_output("lsblk -dpno NAME", shell=True, text=True, stderr=subprocess.DEVNULL).splitlines()
            for d in drives:
                try:
                    res = subprocess.check_output(f"sudo smartctl -H {d}", shell=True, text=True, stderr=subprocess.DEVNULL)
                    status = "HEALTHY" if "PASSED" in res else "WARNING"
                    health_data.append({"drive": d, "status": status})
                except:
                    health_data.append({"drive": d, "status": "UNKNOWN (No SMART support)"})
        except: pass
        return health_data

    def scan_unsafe_permissions(self, home_path):
        """Finds world-writable files in Home (Security risk)."""
        risks = []
        for root, dirs, files in os.walk(home_path):
            # Limit depth for performance
            if root.count(os.sep) - home_path.count(os.sep) > 3:
                continue
            for f in files:
                try:
                    path = os.path.join(root, f)
                    mode = os.stat(path).st_mode
                    if mode & stat.S_IWOTH: # World writable
                        risks.append({"name": f, "path": path, "type": "Unsafe Permission"})
                except: pass
        return risks

    def check_malware_service(self):
        """Checks if ClamAV or similar is installed."""
        import shutil
        return {
            "ClamAV": shutil.which("clamscan") is not None,
            "Rkhunter": shutil.which("rkhunter") is not None
        }
