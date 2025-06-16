#!/bin/bash

echo "Verificando status do PostgreSQL..."
systemctl status postgresql

echo "Listando bancos de dados..."
PGPASSWORD=taleon123 psql -h localhost -U taleon -d postgres -c "\l"

echo "Verificando conexão com o banco taleontracker..."
PGPASSWORD=taleon123 psql -h localhost -U taleon -d taleontracker -c "\dt"

echo "Verificando permissões do usuário taleon..."
sudo -u postgres psql -c "\du taleon"

echo "Verificando configuração do pg_hba.conf..."
cat /etc/postgresql/*/main/pg_hba.conf

echo "Verificando logs do PostgreSQL..."
tail -n 20 /var/log/postgresql/postgresql-*.log 