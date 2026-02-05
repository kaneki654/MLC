import getpass
import subprocess

def get_password(prompt="[MLC] Enter sudo password: "):
    """Securely get password from terminal."""
    try:
        return getpass.getpass(prompt)
    except Exception:
        return None

def verify_sudo(password):
    """Verify if the password is correct by running a simple sudo command."""
    try:
        proc = subprocess.Popen(
            ["sudo", "-S", "-p", "", "true"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        proc.communicate(input=f"{password}\n")
        return proc.returncode == 0
    except:
        return False
