import paramiko
import json
import sys
import os

HOSTS = [
    {
        "name": "nuc-100",
        "host": "nuc-100",
        "user": "copilot",
        "key_path": sys.argv[1] if len(sys.argv) > 1 else None
    },
    {
        "name": "dsk-001",
        "host": "dsk-001",
        "user": "copilot",
        "key_path": sys.argv[1] if len(sys.argv) > 1 else None
    }
]

INFO_COMMANDS = {
    "os_release": "cat /etc/os-release",
    "cpu": "nproc",
    "ram": "free -m",
    "disk": "df -h /",
    "docker": "docker --version || echo 'not installed'",
    "compose": "docker compose version || echo 'not installed'",
    "python": "python3 --version || echo 'not installed'",
    "git": "git --version || echo 'not installed'",
    "curl": "curl --version || echo 'not installed'",
    "ssh": "ssh -V 2>&1 || echo 'not installed'"
}

def gather_info(host, key_path):
    info = {}
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host['host'], username=host['user'], key_filename=key_path)
        for k, cmd in INFO_COMMANDS.items():
            stdin, stdout, stderr = ssh.exec_command(cmd)
            info[k] = stdout.read().decode().strip()
        ssh.close()
    except Exception as e:
        info['error'] = str(e)
    return info

def main():
    key_path = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/.ssh/copilot_ed25519')
    for host in HOSTS:
        host['key_path'] = key_path
        info = gather_info(host, key_path)
        with open(f"{host['name']}_info.json", "w") as f:
            json.dump(info, f, indent=2)
        print(f"Info for {host['name']} written to {host['name']}_info.json")

if __name__ == "__main__":
    main()
