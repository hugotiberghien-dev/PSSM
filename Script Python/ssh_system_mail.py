import paramiko
from datetime import datetime
import mysql.connector 
import smtplib
from email.mime.text import MIMEText

# Connexion MariaDB
db_ip = "192.168.198.157"
db_port = 3306
db_user = "monitor"
db_password = "125136"
db_name = "monitoring"

# Seuils d'alerte
SEUIL_CPU = 70
SEUIL_RAM = 80
SEUIL_DISQUE = 90

# Mail
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "hugo.tiberghien@laplateforme.io"
smtp_password = "jupk exsw cxml qmwb"
mail_dest = "hugo.tiberghien@laplateforme.io"

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

# Vérifier si un mail a déjà été envoyé dans la dernière heure
cursor.execute("SELECT date_envoi FROM derniere_alerte ORDER BY date_envoi DESC LIMIT 1")
dernier_envoi = cursor.fetchone()

peut_envoyer = True
if dernier_envoi:
    diff = datetime.now() - dernier_envoi[0]
    if diff.total_seconds() < 3600:
        peut_envoyer = False
        print("Mail déjà envoyé il y a moins d'une heure — pas d'envoi")

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

    # Vérification des seuils et construction du message d'alerte
    alertes = []
    if cpu > SEUIL_CPU:
        alertes.append(f"CPU trop élevé : {cpu}% (seuil : {SEUIL_CPU}%)")
    if ram > SEUIL_RAM:
        alertes.append(f"RAM trop élevée : {ram:.1f}% (seuil : {SEUIL_RAM}%)")
    if disque > SEUIL_DISQUE:
        alertes.append(f"Disque trop plein : {disque}% (seuil : {SEUIL_DISQUE}%)")

    # Envoi du mail si une alerte et si pas de mail envoyé dans la dernière heure
    if alertes and peut_envoyer:
        contenu = f"Alertes sur le serveur {serveur['nom']} :\n\n"
        contenu += "\n".join(alertes)

        msg = MIMEText(contenu)
        msg["Subject"] = f"Alerte serveur {serveur['nom']}"
        msg["From"] = smtp_user
        msg["To"] = mail_dest

        serveur_smtp = smtplib.SMTP(smtp_host, smtp_port)
        serveur_smtp.starttls()
        serveur_smtp.login(smtp_user, smtp_password)
        serveur_smtp.send_message(msg)
        serveur_smtp.quit()
        print(f"Mail d'alerte envoyé pour {serveur['nom']}")

        cursor.execute("INSERT INTO derniere_alerte (date_envoi) VALUES (%s)", (datetime.now(),))
        db.commit()
        peut_envoyer = False

    client.close()

db.commit()

# Supprimer les entrées de plus de 72h
cursor.execute("DELETE FROM system_status WHERE date_mesure < NOW() - INTERVAL 72 HOUR")
db.commit()
print("Entrées de plus de 72h supprimées")

cursor.close()
db.close()