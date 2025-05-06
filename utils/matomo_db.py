#!/usr/bin/env python3
import os
import subprocess
import datetime

# === CONFIGURAÇÕES ===
DB_USER = "root"
DB_PASSWORD = "root_secret"
DB_NAME = "matomo"
BACKUP_DIR = "/opt/matomo/backups_DB"
DOCKER_DB_CONTAINER = "matomo-db"
DATE = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

BACKUP_FILE = f"{BACKUP_DIR}/matomo_backup_{DATE}.sql.gz"
LOG_DIR = f"{BACKUP_DIR}/logs"
EXPORT_LOG = f"{LOG_DIR}/export_{DATE}.log"
IMPORT_LOG = f"{LOG_DIR}/import_{DATE}.log"


# === FUNÇÕES ===
def export_db():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"📦 A fazer backup da base de dados para: {BACKUP_FILE}")

    cmd = f"sudo mysqldump -u{DB_USER} -p{DB_PASSWORD} {DB_NAME} | gzip > {BACKUP_FILE}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    with open(EXPORT_LOG, "wb") as log_file:
        log_file.write(result.stdout)
        log_file.write(result.stderr)

    if result.returncode == 0:
        print("✅ Backup concluído com sucesso!")
        print(f"📄 Log de exportação: {EXPORT_LOG}")
    else:
        print("❌ Erro ao fazer backup!")
        print(f"📄 Ver log de exportação: {EXPORT_LOG}")


def import_db():
    os.makedirs(LOG_DIR, exist_ok=True)
    file_path = input("🗂 Caminho para o ficheiro de backup (.sql ou .sql.gz): ").strip()

    if not os.path.isfile(file_path):
        print("❌ Ficheiro não encontrado!")
        return

    if file_path.endswith(".gz"):
        # Comprimir e enviar diretamente para o container
        cmd = f"gunzip -c {file_path} | docker exec -i {DOCKER_DB_CONTAINER} mysql -u{DB_USER} -p{DB_PASSWORD} {DB_NAME}"
    else:
        cmd = f"docker exec -i {DOCKER_DB_CONTAINER} mysql -u{DB_USER} -p{DB_PASSWORD} {DB_NAME} < {file_path}"

    print(f"♻️ A importar base de dados de: {file_path}")
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    with open(IMPORT_LOG, "wb") as log_file:
        log_file.write(result.stdout)
        log_file.write(result.stderr)

    if result.returncode == 0:
        print("✅ Importação concluída com sucesso!")
        print(f"📄 Log de importação: {IMPORT_LOG}")
    else:
        print("❌ Erro ao importar a base de dados!")
        print(f"📄 Ver log de importação: {IMPORT_LOG}")


# === MENU ===
def main():
    print("🛠 Script de Backup/Importação da Base de Dados Matomo")
    print("1. Exportar base de dados")
    print("2. Importar base de dados")
    option = input("Escolha a opção (1 ou 2): ").strip()

    if option == "1":
        export_db()
    elif option == "2":
        import_db()
    else:
        print("❌ Opção inválida.")


if __name__ == "__main__":
    main()
