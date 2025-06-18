#!/bin/bash

# Atualizar o sistema
apt update
apt upgrade -y

# Instalar dependências
apt install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev git npm nodejs 

# Criar e ativar ambiente virtual
python3 -m venv /opt/taleontracker/venv
source /opt/taleontracker/venv/bin/activate

# Instalar dependências Python
pip install -r /opt/taleontracker/backend/requirements.txt

# Configurar PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE taleontracker;"
sudo -u postgres psql -c "CREATE USER taleon WITH PASSWORD 'taleon123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE taleontracker TO taleon;"

# Configurar o serviço
cp /opt/taleontracker/backend/taleontracker.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable taleontracker
systemctl start taleontracker

# Inicializar o banco de dados
cd /opt/taleontracker/backend
python3 init_db.py

echo "Instalação concluída!"
