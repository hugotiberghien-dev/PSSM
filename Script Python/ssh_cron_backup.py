import paramiko
from datetime import datetime

# Connexion SSH
ssh_ip = "192.168.198.157"
ssh_port = 22
ssh_user = "monitor"
ssh_key = "/home/monitor/.ssh/monitor_key"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=ssh_ip, port=ssh_port, username=ssh_user, key_filename=ssh_key)

date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nom_backup = f"/home/monitor/backups/backup_{date}.sql"

# Créer le dossier backups si il n'existe pas
client.exec_command("mkdir -p /home/monitor/backups")

# Lancer la sauvegarde
commande = f"mysqldump -u monitor -p125136 monitoring > {nom_backup}"
stdin, stdout, stderr = client.exec_command(commande)
stdout.channel.recv_exit_status()

print(f"Sauvegarde créée : {nom_backup}")

# Garder uniquement les 7 dernières sauvegardes
stdin, stdout, stderr = client.exec_command("ls -t /home/monitor/backups/backup_*.sql")
fichiers = stdout.read().decode().strip().split("\n")

if len(fichiers) > 7:
    for fichier in fichiers[7:]:
        client.exec_command(f"rm {fichier}")
        print(f"Ancienne sauvegarde supprimée : {fichier}")

client.close()