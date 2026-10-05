import paramiko
import mysql.connector
import re

# Connexion SSH
ssh_ip = "192.168.198.157"
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/monitor/.ssh/monitor_key"

# Connexion MariaDB
db_ip = "192.168.198.157"
db_port = 3306
db_user = "monitor"
db_password = "125136"
db_name = "monitoring"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=ssh_ip, port=ssh_port, username=ssh_user, key_filename=ssh_key)
stdin, stdout, stderr = client.exec_command("sudo journalctl -u mariadb | grep 'Access denied'")

logs = stdout.read().decode()
pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \d+ \[Warning\] Access denied for user '(\w+)'@'([\d.]+)'"
resultats = re.findall(pattern, logs)

db = mysql.connector.connect(
    host=db_ip,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = db.cursor()

for date, utilisateur, ip in resultats:
    cursor.execute(
        "INSERT INTO logs_mysql (utilisateur, ip, date_tentative) VALUES (%s, %s, %s)",
        (utilisateur, ip, date)
    )

db.commit()
print(f"{len(resultats)} entrées insérées dans la base de données")

cursor.close()
db.close()
client.close()