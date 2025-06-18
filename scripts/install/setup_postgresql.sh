#!/bin/bash

# Verificar se o PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    echo "Instalando PostgreSQL..."
    apt-get update
    apt-get install -y postgresql postgresql-contrib
fi

# Garantir que o PostgreSQL está rodando
systemctl start postgresql
systemctl enable postgresql

# Verificar status
echo "Verificando status do PostgreSQL..."
systemctl status postgresql

# Configurar o usuário e banco de dados
echo "Configurando usuário e banco de dados..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS taleontracker;
DROP USER IF EXISTS taleon;
CREATE USER taleon WITH PASSWORD 'taleon123' CREATEDB;
CREATE DATABASE taleontracker OWNER taleon;
\c taleontracker
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO taleon;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO taleon;
GRANT ALL PRIVILEGES ON SCHEMA public TO taleon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO taleon;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO taleon;
EOF

# Configurar autenticação
echo "Configurando autenticação..."
cat > /etc/postgresql/*/main/pg_hba.conf << EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5
EOF

# Reiniciar PostgreSQL
echo "Reiniciando PostgreSQL..."
systemctl restart postgresql

# Aguardar o PostgreSQL iniciar
sleep 5

# Testar conexão
echo "Testando conexão..."
PGPASSWORD=taleon123 psql -h localhost -U taleon -d taleontracker -c "\l"

# Verificar se o usuário foi criado
echo "Verificando usuário..."
sudo -u postgres psql -c "\du"

echo "Configuração do PostgreSQL concluída!" 