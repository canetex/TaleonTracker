#!/bin/bash

# Criar usuário e banco de dados
sudo -u postgres psql << EOF
CREATE USER taleon WITH PASSWORD 'taleon123';
CREATE DATABASE taleontracker;
GRANT ALL PRIVILEGES ON DATABASE taleontracker TO taleon;
\c taleontracker
GRANT ALL ON SCHEMA public TO taleon;
EOF

# Configurar autenticação
echo "local   all             taleon                                  md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
echo "host    all             taleon          127.0.0.1/32            md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
echo "host    all             taleon          ::1/128                 md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf

# Reiniciar PostgreSQL
systemctl restart postgresql

# Verificar status
systemctl status postgresql

# Testar conexão
PGPASSWORD=taleon123 psql -U taleon -d taleontracker -c "\l" 