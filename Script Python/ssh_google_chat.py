import requests
import paramiko
from datetime import datetime

# Webhook Google Chat
WEBHOOK_URL = "https://chat.googleapis.com/v1/spaces/AAQAIey_OOE/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=rPYStTPLdYMf4eZBTXqErPtNELMHXbOdqpWu1Y3Oo-o"

# Serveurs
serveurs = [
    {"nom": "ftp", "ip": "192.168.198.155"},
    {"nom": "web", "ip": "192.168.198.156"},
    {"nom": "sql", "ip": "192.168.198.157"}
]

# SSH
ssh_key = "/home/monitor/.ssh/monitor_key"
ssh_user = "monitor"
ssh_port = 22

# Construction du message
message = f" *Rapport système du {datetime.now().strftime('%d/%m/%Y %H:%M')}*\n\n"

for serveur in serveurs:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=serveur["ip"], port=ssh_port, username=ssh_user, key_filename=ssh_key)

    # CPU
    stdin, stdout, stderr = client.exec_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    cpu = float(stdout.read().decode().strip().replace(',', '.'))

    # RAM
    stdin, stdout, stderr = client.exec_command("free | grep Mem | awk '{print $3/$2 * 100}'")
    ram = float(stdout.read().decode().strip().replace(',', '.'))

    # Disque
    stdin, stdout, stderr = client.exec_command("df / | tail -1 | awk '{print $5}' | tr -d '%'")
    disque = float(stdout.read().decode().strip().replace(',', '.'))

    message += f"*Serveur {serveur['nom']}*\n"
    message += f"  CPU: {cpu}%\n"
    message += f"  RAM: {ram:.1f}%\n"
    message += f"  Disque: {disque}%\n\n"

    client.close()

# Envoi du message dans Google Chat
response = requests.post(WEBHOOK_URL, json={"text": message})

if response.status_code == 200:
    print("Message envoyé dans Google Chat")
else:
    print(f"Erreur : {response.status_code}")

