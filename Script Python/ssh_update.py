import paramiko
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# Mail
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "hugo.tiberghien@laplateforme.io"
smtp_password = "ton_mot_de_passe_application"
mail_dest = "hugo.tiberghien@laplateforme.io"

serveurs = [
    {"nom": "ftp", "ip": "192.168.198.155"},
    {"nom": "web", "ip": "192.168.198.156"},
    {"nom": "sql", "ip": "192.168.198.157"}
]

ssh_key = "/home/monitor/.ssh/monitor_key"
ssh_user = "monitor"
ssh_port = 22

for serveur in serveurs:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=serveur["ip"], port=ssh_port, username=ssh_user, key_filename=ssh_key)

    print(f"\n=== Serveur {serveur['nom']} ===")

    # Vérifier les mises à jour disponibles
    stdin, stdout, stderr = client.exec_command("sudo apt update 2>/dev/null && apt list --upgradable 2>/dev/null | grep -v 'Listing'")
    mises_a_jour = stdout.read().decode().strip()

    if mises_a_jour:
        print(f"Mises à jour disponibles :\n{mises_a_jour}")

        # Appliquer les mises à jour
        stdin, stdout, stderr = client.exec_command("sudo apt upgrade -y 2>/dev/null")
        stdout.channel.recv_exit_status()
        print("Mises à jour appliquées")
    else:
        print("Aucune mise à jour disponible")

    # Vérifier si un redémarrage est nécessaire
    stdin, stdout, stderr = client.exec_command("[ -f /var/run/reboot-required ] && echo 'reboot_required' || echo 'no_reboot'")
    reboot = stdout.read().decode().strip()

    if reboot == "reboot_required":
        print(f"Redémarrage requis sur {serveur['nom']}")

        # Envoi du mail
        contenu = f"Le serveur {serveur['nom']} ({serveur['ip']}) nécessite un redémarrage après mise à jour."
        msg = MIMEText(contenu)
        msg["Subject"] = f"Redémarrage requis — {serveur['nom']}"
        msg["From"] = smtp_user
        msg["To"] = mail_dest

        serveur_smtp = smtplib.SMTP(smtp_host, smtp_port)
        serveur_smtp.starttls()
        serveur_smtp.login(smtp_user, smtp_password)
        serveur_smtp.send_message(msg)
        serveur_smtp.quit()
        print(f"Mail envoyé pour {serveur['nom']}")
    else:
        print(f"Pas de redémarrage requis sur {serveur['nom']}")

    client.close()

print("\nMises à jour terminées sur tous les serveurs")