import subprocess
import os

class PackageManager:
    def get_orphaned_configs(self):
        """Finds config files left by uninstalled deb packages."""
        orphans = []
        try:
            # dpkg -l shows 'rc' for packages that are removed but configs remain
            res = subprocess.check_output("dpkg -l | grep '^rc' | awk '{print $2}'", shell=True, text=True, stderr=subprocess.DEVNULL)
            for pkg in res.splitlines():
                if pkg:
                    orphans.append({"name": pkg, "type": "DEB Config", "size": 0})
        except: pass
        return orphans

    def purge_orphans(self, packages):
        count = 0
        for pkg in packages:
            try:
                subprocess.run(f"sudo dpkg --purge {pkg}", shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                count += 1
            except: pass
        return count

    def get_unused_runtimes(self):
        """Detects unused Flatpak runtimes."""
        unused = []
        try:
            res = subprocess.check_output("flatpak list --unused --columns=name,application", shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in res.splitlines():
                if line:
                    unused.append({"name": line.strip(), "type": "Flatpak Runtime"})
        except: pass
        return unused
