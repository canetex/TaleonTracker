#!/bin/bash

echo "Encerrando todas as conexões com o banco de dados..."
sudo -u postgres psql << EOF
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'taleontracker'
AND pid <> pg_backend_pid();
EOF

echo "Removendo banco de dados e usuário..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS taleontracker;
DROP USER IF EXISTS taleon;
EOF

echo "Reiniciando PostgreSQL..."
systemctl restart postgresql

echo "Aguardando PostgreSQL iniciar..."
sleep 5

echo "Executando setup do PostgreSQL..."
./setup_postgresql.sh

echo "Executando setup do banco de dados..."
./setup_database.sh

echo "Verificando status do PostgreSQL..."
systemctl status postgresql

echo "Verificando conexão..."
PGPASSWORD=taleon123 psql -h localhost -U taleon -d taleontracker -c "\l" 