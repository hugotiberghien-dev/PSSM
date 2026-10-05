import paramiko

ip = "192.168.198.157"
port = 22
user = "monitor"
key_path = "/home/monitor/.ssh/monitor_key"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=ip, port=port, username=user, key_filename=key_path)
stdin, stdout, stderr = client.exec_command("mysql -u monitor -p125136 -e 'SHOW DATABASES;'")
print(stdout.read().decode())
client.close()