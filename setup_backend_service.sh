#!/bin/bash

# Criar diretório de instalação
mkdir -p /opt/taleontracker/backend

# Copiar arquivos do backend
cp -r backend/* /opt/taleontracker/backend/

# Copiar arquivo de serviço
cp backend/taleontracker.service /etc/systemd/system/

# Recarregar systemd
systemctl daemon-reload

# Habilitar e iniciar o serviço
systemctl enable taleontracker.service
systemctl start taleontracker.service

# Verificar status
systemctl status taleontracker.service 