#!/bin/bash

# Instalar Node.js e npm se não estiverem instalados
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

# Instalar serve globalmente
npm install -g serve

# Criar diretório de instalação
mkdir -p /opt/taleontracker/frontend

# Copiar arquivos do frontend
cp -r frontend/* /opt/taleontracker/frontend/

# Instalar dependências e fazer build
cd /opt/taleontracker/frontend
npm install
npm run build

# Copiar arquivo de serviço
cp /root/TaleonTracker/frontend/taleontracker-frontend.service /etc/systemd/system/

# Recarregar systemd
systemctl daemon-reload

# Habilitar e iniciar o serviço
systemctl enable taleontracker-frontend.service
systemctl start taleontracker-frontend.service

# Verificar status
systemctl status taleontracker-frontend.service 