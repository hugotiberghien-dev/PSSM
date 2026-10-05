import paramiko
from datetime import datetime
import mysql.connector 

# Connexion MariaDB
db_ip = "192.168.198.157"
db_port = 3306
db_user = "monitor"
db_password = "125136"
db_name = "monitoring"

serveurs = [
    {"nom": "ftp", "ip": "192.168.198.155"},
    {"nom": "web", "ip": "192.168.198.156"},
    {"nom": "sql", "ip": "192.168.198.157"}
]

ssh_key = "/home/monitor/.ssh/monitor_key"
ssh_user = "monitor"
ssh_port = 22

db = mysql.connector.connect(
    host=db_ip,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = db.cursor()

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

    # Insertion dans la base
    cursor.execute(
        "INSERT INTO system_status (serveur, cpu, ram, disque, date_mesure) VALUES (%s, %s, %s, %s, %s)",
        (serveur["nom"], cpu, ram, disque, datetime.now())
    )
    print(f"Serveur {serveur['nom']} → CPU: {cpu}% | RAM: {ram:.1f}% | Disque: {disque}%")
    client.close()

db.commit()

# Supprimer les entrées de plus de 72h
cursor.execute("DELETE FROM system_status WHERE date_mesure < NOW() - INTERVAL 72 HOUR")
db.commit()
print("Entrées de plus de 72h supprimées")

cursor.close()
db.close()