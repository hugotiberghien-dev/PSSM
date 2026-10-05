import paramiko

ip = "192.168.198.155"
port = 22
user = "monitor"
key_path = "/home/monitor/.ssh/monitor_key"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=ip, port=port, username=user, key_filename=key_path)
stdin, stdout, stderr = client.exec_command("sudo df -h")
print(stdout.read().decode())
print(stderr.read().decode())
client.close()