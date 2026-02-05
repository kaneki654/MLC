import os
import shutil
import time
import filecmp

class BackupManager:
    def create_snapshot(self, source, backup_root):
        """Creates a 'Zero-Space' backup using hard links."""
        if not os.path.exists(source):
            return False, "Source not found"

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        name = os.path.basename(source) if os.path.basename(source) else "Root"
        dest_dir = os.path.join(backup_root, f"Snapshot_{name}_{timestamp}")
        
        try:
            os.makedirs(dest_dir, exist_ok=True)
            
            # Save metadata
            with open(os.path.join(dest_dir, ".meta"), "w") as f:
                f.write(f"Source: {os.path.abspath(source)}\nTime: {timestamp}")

            if os.path.isfile(source):
                dest_file = os.path.join(dest_dir, name)
                try:
                    os.link(source, dest_file)
                    return True, "Snapshot created (Zero Space)"
                except OSError:
                    shutil.copy2(source, dest_file)
                    return True, "Snapshot created (Copy - Different Drive)"

            count = 0
            linked = 0
            copied = 0
            
            for root, dirs, files in os.walk(source):
                rel_path = os.path.relpath(root, source)
                current_dest_dir = os.path.join(dest_dir, rel_path)
                
                os.makedirs(current_dest_dir, exist_ok=True)
                
                for f in files:
                    src_file = os.path.join(root, f)
                    dst_file = os.path.join(current_dest_dir, f)
                    
                    if os.path.exists(dst_file): continue
                    
                    try:
                        os.link(src_file, dst_file)
                        linked += 1
                    except OSError:
                        try:
                            shutil.copy2(src_file, dst_file)
                            copied += 1
                        except: pass
                    count += 1
            
            return True, f"Success.\nLinked: {linked} (0 space)\nCopied: {copied}"
            
        except Exception as e:
            return False, str(e)

    def restore_snapshot(self, snapshot_path, restore_dest):
        """Restores files from a snapshot to a destination."""
        try:
            # Check if we are restoring a folder or single file structure
            # Snapshot folder usually contains the files directly or hierarchically
            
            # Use copy2 to dereference hardlinks (turn them back into independent files)
            if os.path.isfile(snapshot_path):
                shutil.copy2(snapshot_path, restore_dest)
            else:
                # Copytree requires dest to NOT exist usually, or use dirs_exist_ok in 3.8+
                if os.path.exists(restore_dest):
                    # Merger/Overwrite mode
                    for root, dirs, files in os.walk(snapshot_path):
                        if ".meta" in files: files.remove(".meta")
                        
                        rel = os.path.relpath(root, snapshot_path)
                        dest_dir = os.path.join(restore_dest, rel)
                        os.makedirs(dest_dir, exist_ok=True)
                        for f in files:
                            shutil.copy2(os.path.join(root, f), os.path.join(dest_dir, f))
                else:
                    shutil.copytree(snapshot_path, restore_dest, ignore=shutil.ignore_patterns('.meta'))
            
            return True, "Restore Complete"
        except Exception as e:
            return False, str(e)

    def compare_snapshot(self, snapshot_path, original_source):
        """Checks if insides of files have changed since backup."""
        diffs = []
        if not os.path.exists(original_source):
            return ["Original source missing"]

        # Use dircmp for folders
        dcmp = filecmp.dircmp(original_source, snapshot_path, ignore=['.meta'])
        
        if dcmp.diff_files:
            diffs.append(f"Modified Files: {len(dcmp.diff_files)}")
        if dcmp.left_only:
            diffs.append(f"New Files (Not in backup): {len(dcmp.left_only)}")
        if dcmp.right_only:
            diffs.append(f"Deleted Files (In backup only): {len(dcmp.right_only)}")
            
        return diffs if diffs else ["Perfect Match (No changes)"]
