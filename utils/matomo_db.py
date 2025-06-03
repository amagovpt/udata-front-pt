#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import subprocess
import datetime

# Compatibilidade Python 2 e 3
try:
    compat_input = raw_input  # Python 2
except NameError:
    compat_input = input      # Python 3

# === CONFIGURAÇÕES ===
DB_USER = "root"
DB_PASSWORD = "root_secret"
DB_NAME = "matomo"
BACKUP_DIR = "/opt/matomo/backups_DB"
DOCKER_DB_CONTAINER = "matomo-db"
DATE = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

BACKUP_FILE = "{}/matomo_backup_{}.sql.gz".format(BACKUP_DIR, DATE)
LOG_DIR = "{}/logs".format(BACKUP_DIR)
EXPORT_LOG = "{}/export_{}.log".format(LOG_DIR, DATE)
IMPORT_LOG = "{}/import_{}.log".format(LOG_DIR, DATE)


# === FUNÇÕES ===
def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def run_command(cmd, log_path):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    with open(log_path, "wb") as log_file:
        log_file.write(out)
        log_file.write(err)

    return process.returncode


def export_db():
    make_dir(BACKUP_DIR)
    make_dir(LOG_DIR)
    print("📦 A fazer backup da base de dados para: {}".format(BACKUP_FILE))

    cmd = "sudo mysqldump -u{} -p{} {} | gzip > {}".format(DB_USER, DB_PASSWORD, DB_NAME, BACKUP_FILE)
    returncode = run_command(cmd, EXPORT_LOG)

    if returncode == 0:
        print("✅ Backup concluído com sucesso!")
        print("📄 Log de exportação: {}".format(EXPORT_LOG))
    else:
        print("❌ Erro ao fazer backup!")
        print("📄 Ver log de exportação: {}".format(EXPORT_LOG))


def import_db():
    make_dir(LOG_DIR)
    file_path = compat_input("🗂 Caminho para o ficheiro de backup (.sql ou .sql.gz): ").strip()

    if not os.path.isfile(file_path):
        print("❌ Ficheiro não encontrado!")
        return

    if file_path.endswith(".gz"):
        cmd = "gunzip -c {} | docker exec -i {} mysql -u{} -p{} {}".format(
            file_path, DOCKER_DB_CONTAINER, DB_USER, DB_PASSWORD, DB_NAME)
    else:
        cmd = "docker exec -i {} mysql -u{} -p{} {} < {}".format(
            DOCKER_DB_CONTAINER, DB_USER, DB_PASSWORD, DB_NAME, file_path)

    print("♻️ A importar base de dados de: {}".format(file_path))
    returncode = run_command(cmd, IMPORT_LOG)

    if returncode == 0:
        print("✅ Importação concluída com sucesso!")
        print("📄 Log de importação: {}".format(IMPORT_LOG))
    else:
        print("❌ Erro ao importar a base de dados!")
        print("📄 Ver log de importação: {}".format(IMPORT_LOG))


# === MENU ===
def main():
    print("🛠 Script de Backup/Importação da Base de Dados Matomo")
    print("1. Exportar base de dados")
    print("2. Importar base de dados")
    option = compat_input("Escolha a opção (1 ou 2): ").strip()

    if option == "1":
        export_db()
    elif option == "2":
        import_db()
    else:
        print("❌ Opção inválida.")


if __name__ == "__main__":
    main()
