#!/bin/bash

# Atualiza o sistema
apt update && apt upgrade -y

# Instala dependências necessárias
apt install -y python3 python3-pip python3-venv nginx supervisor

# Cria diretório para a aplicação
mkdir -p /opt/taleontracker
cd /opt/taleontracker

# Clona o repositório
git clone https://github.com/canetex/TaleonTracker.git .

# Configura o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instala dependências
cd backend
pip install -r requirements.txt

# Configura o supervisor
cat > /etc/supervisor/conf.d/taleontracker.conf << EOL
[program:taleontracker]
directory=/opt/taleontracker/backend
command=/opt/taleontracker/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/taleontracker.err.log
stdout_logfile=/var/log/taleontracker.out.log
EOL

# Configura o serviço systemd
cat > /etc/systemd/system/taleontracker.service << EOL
[Unit]
Description=TaleonTracker API Service
After=network.target

[Service]
User=root
WorkingDirectory=/opt/taleontracker/backend
Environment="PATH=/opt/taleontracker/venv/bin"
ExecStart=/opt/taleontracker/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

# Configura o Nginx
cat > /etc/nginx/sites-available/taleontracker << EOL
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Ativa o site no Nginx
ln -s /etc/nginx/sites-available/taleontracker /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Reinicia os serviços
systemctl daemon-reload
systemctl enable taleontracker
systemctl start taleontracker
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl start taleontracker

# Configura o serviço para iniciar com o sistema
systemctl enable nginx
systemctl enable supervisor 