import os
import subprocess
import shutil

class SystemOptimizer:
    def __init__(self, theme, auth_callback=None):
        self.theme = theme
        self.auth_callback = auth_callback

    def _run_privileged(self, command):
        """Runs a command with sudo -S using the app's password dialog."""
        if not self.auth_callback:
            return False, "Internal Error: No auth callback."
            
        password = self.auth_callback()
        if password is None:
            return False, "Authentication cancelled."

        try:
            # -S reads password from stdin, -p '' suppresses prompt
            proc = subprocess.Popen(
                ["sudo", "-S", "-p", "", "sh", "-c", command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(input=f"{password}\n")
            
            if proc.returncode == 0:
                return True, "Operation successful."
            else:
                return False, f"System Error: {stderr.strip() or 'Permission Denied'}"
        except Exception as e:
            return False, str(e)

    def drop_caches(self):
        """Flushes RAM PageCache using sudo."""
        # Use tee to write to protected file safely
        cmd = "sync && echo 3 | tee /proc/sys/vm/drop_caches"
        success, msg = self._run_privileged(cmd)
        if success: return True, "RAM Cache flushed successfully."
        return False, msg

    def optimize_swap(self):
        """Refreshes swap using sudo."""
        import psutil
        mem = psutil.virtual_memory()
        if mem.available < psutil.swap_memory().used:
            return False, "Risk: Not enough free RAM to safe-swap."
            
        # Use full paths for reliability
        cmd = "/sbin/swapoff -a && /sbin/swapon -a"
        success, msg = self._run_privileged(cmd)
        if success: return True, "Swap memory defragmented."
        return False, msg

    def set_governor(self, mode):
        """Sets swappiness using sudo."""
        if mode == "performance":
            val = 10
            profile = "Gaming Mode (Swap: 10)"
        elif mode == "battery":
            val = 90
            profile = "Battery Saver (Swap: 90)"
        else:
            val = 60
            profile = "Balanced Mode (Swap: 60)"
            
        cmd = f"/sbin/sysctl -w vm.swappiness={val}"
        success, msg = self._run_privileged(cmd)
        if success: return True, f"{profile} Active."
        return False, msg

class StartupManager:
    def list_autostart(self):
        """Lists XDG autostart entries."""
        apps = []
        path = os.path.expanduser("~/.config/autostart")
        if os.path.exists(path):
            for f in os.listdir(path):
                if f.endswith(".desktop"):
                    apps.append({"name": f.replace(".desktop", ""), "path": os.path.join(path, f), "enabled": True})
        return apps

    def toggle_app(self, path, enable=True):
        try:
            if not enable:
                # Add Hidden=true to desktop file
                with open(path, "a") as f: f.write("\nHidden=true\n")
            return True
        except: return False
