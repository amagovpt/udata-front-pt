#!/bin/bash

# Script para instalação e configuração do logrotate

echo "Iniciando instalação e configuração do logrotate..."

# 1. Instalar o logrotate
echo "1. Instalando o logrotate..."
sudo yum install -y logrotate

echo "1.1 Verificando a instalação do logrotate..."
if logrotate --version &>/dev/null; then
    echo "Logrotate instalado com sucesso. Versão: $(logrotate --version | head -n 1)"
else
    echo "Falha na instalação do logrotate. Verifique o ambiente."
    exit 1
fi

# 2. Criar o arquivo de configuração do logrotate
CONFIG_PATH="/etc/logrotate.d/uwsgi_logs"
echo "2. Criando arquivo de configuração em $CONFIG_PATH..."
sudo bash -c "cat > $CONFIG_PATH" <<EOL
/home/udata/logs/app.logs {
    su root root
    daily
    rotate 30
    compress
    missingok
    notifempty
    dateext
    dateformat .%Y-%m-%d
    copytruncate
    postrotate
        : > /home/udata/logs/app.logs
        systemctl reload uwsgi > /dev/null 2>&1 || true
    endscript
}
EOL
echo "Arquivo de configuração criado."

# 3. Testar a configuração do logrotate
echo "3. Testando a configuração do logrotate..."
echo "3.1 Simulando a rotação de logs..."
sudo logrotate -d "$CONFIG_PATH"

echo "3.2 Forçando a rotação de logs..."
sudo logrotate -f "$CONFIG_PATH"

# 4. Verificar os arquivos de log após a rotação
echo "4. Verificando os arquivos de log rotacionados..."
ls /home/udata/logs/

# 5. Configurar a execução automática com cron
echo "5. Configurando a execução automática com cron..."
CRON_PATH="/etc/cron.daily/logrotate"
if [ -f "$CRON_PATH" ]; then
    echo "Cron job já configurado em $CRON_PATH."
else
    echo "Adicionando cron job..."
    sudo bash -c "echo '10 0 * * * /usr/sbin/logrotate /etc/logrotate.conf' >> /var/spool/cron/root"
    echo "Cron job adicionado com sucesso."
fi

# 6. Verificar a execução automática de cron
echo "6. Verificando a execução automática de cron..."
sudo run-parts /etc/cron.daily/

echo "Verifique os logs do cron para validar a execução:"
sudo cat /var/log/cron

echo "Configuração do logrotate concluída com sucesso."
