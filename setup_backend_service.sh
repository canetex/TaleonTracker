#!/bin/bash

# Instala dependências do sistema
apt-get update
apt-get install -y python3-venv python3-pip nginx redis-server

# Configura o Redis
systemctl enable redis-server
systemctl start redis-server

# Cria diretório para o backend
mkdir -p /opt/taleontracker/backend

# Cria e ativa ambiente virtual
python3 -m venv /opt/taleontracker/backend/venv
source /opt/taleontracker/backend/venv/bin/activate

# Instala dependências Python
pip install --upgrade pip
pip install -r /opt/taleontracker/backend/requirements.txt

# Configura o serviço systemd
cat > /etc/systemd/system/taleontracker.service << EOL
[Unit]
Description=TaleonTracker Backend Service
After=network.target postgresql.service redis-server.service

[Service]
User=root
WorkingDirectory=/opt/taleontracker/backend
Environment="PATH=/opt/taleontracker/backend/venv/bin"
ExecStart=/opt/taleontracker/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Recarrega systemd e inicia o serviço
systemctl daemon-reload
systemctl enable taleontracker
systemctl start taleontracker

# Verificar status
systemctl status taleontracker.service 