import paramiko
import mysql.connector
import re

# Connexion SSH
ssh_ip = "192.168.198.155"
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
stdin, stdout, stderr = client.exec_command("sudo cat /var/log/vsftpd.log")

logs = stdout.read().decode()
pattern = r"(\w+ \w+ \d+ \d+:\d+:\d+ \d+) \[pid \d+\] \[(\w+)\] FAIL LOGIN: Client \"::ffff:([\d.]+)\""
resultats = re.findall(pattern, logs)

db = mysql.connector.connect(
    host=db_ip,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = db.cursor()

from datetime import datetime

for date, utilisateur, ip in resultats:
    date_convertie = datetime.strptime(date, "%a %b %d %H:%M:%S %Y")
    cursor.execute(
        "INSERT INTO logs_ftp (utilisateur, ip, date_tentative) VALUES (%s, %s, %s)",
        (utilisateur, ip, date_convertie)
    )
db.commit()
print(f"{len(resultats)} entrées insérées dans la base de données")

cursor.close()
db.close()
client.close()