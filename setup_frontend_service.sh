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

# Obter o IP atual da máquina
CURRENT_IP=$(hostname -I | awk '{print $1}')

# Configurar variáveis de ambiente
cd /opt/taleontracker/frontend
echo "REACT_APP_API_URL=http://${CURRENT_IP}:8000" > .env

# Instalar dependências
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