#!/bin/bash

# Ativar o ambiente virtual
source /opt/taleontracker/venv/bin/activate

# Navegar até o diretório do backend
cd /opt/taleontracker/backend

# Executar o script de inicialização do banco de dados
python3 init_db.py

# Verificar se o PostgreSQL está rodando
systemctl status postgresql

# Verificar as tabelas no banco de dados
PGPASSWORD=taleon123 psql -h localhost -U taleon -d taleontracker -c "\dt"
PGPASSWORD=taleon123 psql -h localhost -U taleon -d taleontracker -c "\d characters"
PGPASSWORD=taleon123 psql -h localhost -U taleon -d taleontracker -c "\d character_history" 