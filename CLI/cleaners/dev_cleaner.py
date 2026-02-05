import os
import shutil
import subprocess

class DevCleaner:
    def scan_dev_junk(self, user_path):
        results = []
        home = os.path.expanduser("~")
        
        # 1. Python Pip Cache
        pip = os.path.join(home, ".cache", "pip")
        if os.path.exists(pip):
            results.append({"name": "Pip Cache", "path": pip, "size": self._get_size(pip), "type": "Dev Junk"})

        # 2. NPM / Yarn Cache
        npm = os.path.join(home, ".npm")
        if os.path.exists(npm):
            results.append({"name": "NPM Cache", "path": npm, "size": self._get_size(npm), "type": "Dev Junk"})
            
        yarn = os.path.join(home, ".cache", "yarn")
        if os.path.exists(yarn):
            results.append({"name": "Yarn Cache", "path": yarn, "size": self._get_size(yarn), "type": "Dev Junk"})

        # 3. Cargo (Rust) Registry
        cargo = os.path.join(home, ".cargo", "registry")
        if os.path.exists(cargo):
            results.append({"name": "Cargo Registry", "path": cargo, "size": self._get_size(cargo), "type": "Dev Junk"})

        # 4. Gradle Cache
        gradle = os.path.join(home, ".gradle", "caches")
        if os.path.exists(gradle):
             results.append({"name": "Gradle Cache", "path": gradle, "size": self._get_size(gradle), "type": "Dev Junk"})

        return results

    def prune_docker(self):
        """Runs docker system prune -f"""
        try:
            # Try user mode first, might fail if group not set
            subprocess.run(["docker", "system", "prune", "-f", "--volumes"], check=True)
            return True
        except: return False

    def _get_size(self, path):
        total = 0
        try:
            for root, dirs, files in os.walk(path):
                for f in files:
                    try: total += os.path.getsize(os.path.join(root, f))
                    except: pass
        except: pass
        return total
