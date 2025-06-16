#!/bin/bash

# Instalar Node.js e npm se não estiverem instalados
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

# Instalar PM2 globalmente
npm install -g pm2

# Criar diretório de instalação
mkdir -p /opt/taleontracker/frontend

# Copiar arquivos do frontend
cp -r frontend/* /opt/taleontracker/frontend/

# Instalar dependências
cd /opt/taleontracker/frontend
npm install

# Configurar PM2 para gerenciar o frontend
pm2 start npm --name "taleontracker-frontend" -- start

# Configurar PM2 para iniciar automaticamente com o sistema
pm2 startup
pm2 save

# Verificar status
pm2 status

# Mostrar logs
echo "Logs do frontend:"
pm2 logs taleontracker-frontend --lines 10 