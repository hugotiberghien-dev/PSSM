import mysql.connector
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

# Connexion MariaDB
db_ip = "192.168.198.157"
db_port = 3306
db_user = "monitor"
db_password = "125136"
db_name = "monitoring"

# Mail
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "hugo.tiberghien@laplateforme.io"
smtp_password = "jupk exsw cxml qmwb"
mail_dest = "hugo.tiberghien@laplateforme.io"

# Date de la veille
hier = datetime.now() - timedelta(days=1)
hier_debut = hier.replace(hour=0, minute=0, second=0)
hier_fin = hier.replace(hour=23, minute=59, second=59)

# Connexion MariaDB
db = mysql.connector.connect(
    host=db_ip,
    port=db_port,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = db.cursor()

# Récupération des logs de la veille
cursor.execute("SELECT utilisateur, ip, date_tentative FROM logs_mysql WHERE date_tentative BETWEEN %s AND %s", (hier_debut, hier_fin))
logs_mysql = cursor.fetchall()

cursor.execute("SELECT utilisateur, ip, date_tentative FROM logs_ftp WHERE date_tentative BETWEEN %s AND %s", (hier_debut, hier_fin))
logs_ftp = cursor.fetchall()

cursor.execute("SELECT utilisateur, ip, date_tentative FROM logs_web WHERE date_tentative BETWEEN %s AND %s", (hier_debut, hier_fin))
logs_web = cursor.fetchall()

# Construction du mail
contenu = f"Rapport des tentatives de connexion du {hier.strftime('%d/%m/%Y')}\n\n"

contenu += f"=== Serveur SQL ({len(logs_mysql)} tentatives) ===\n"
for utilisateur, ip, date in logs_mysql:
    contenu += f"  - {date} | utilisateur: {utilisateur} | IP: {ip}\n"

contenu += f"\n=== Serveur FTP ({len(logs_ftp)} tentatives) ===\n"
for utilisateur, ip, date in logs_ftp:
    contenu += f"  - {date} | utilisateur: {utilisateur} | IP: {ip}\n"

contenu += f"\n=== Serveur Web ({len(logs_web)} tentatives) ===\n"
for utilisateur, ip, date in logs_web:
    contenu += f"  - {date} | utilisateur: {utilisateur} | IP: {ip}\n"


# Envoi du mail
msg = MIMEText(contenu)
msg["Subject"] = f"Rapport sécurité du {hier.strftime('%d/%m/%Y')}"
msg["From"] = smtp_user
msg["To"] = mail_dest

serveur = smtplib.SMTP(smtp_host, smtp_port)
serveur.starttls()
serveur.login(smtp_user, smtp_password)
serveur.send_message(msg)
serveur.quit()

print("Mail envoyé avec succès")

cursor.close()
db.close()