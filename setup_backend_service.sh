#!/bin/bash

# Criar diretório de instalação
mkdir -p /opt/taleontracker/backend

# Copiar arquivos do backend
cp -r backend/* /opt/taleontracker/backend/

# Configurar ambiente virtual e instalar dependências
cd /opt/taleontracker/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copiar arquivo de serviço
cp backend/taleontracker.service /etc/systemd/system/

# Recarregar systemd
systemctl daemon-reload

# Habilitar e iniciar o serviço
systemctl enable taleontracker.service
systemctl restart taleontracker.service

# Verificar status
systemctl status taleontracker.service 