#!/bin/bash

# Configurações do Banco de Dados
DB_NAME=taleontracker
DB_USER=taleon
DB_HOST=localhost
DB_PORT=5432

# Configurações do Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Configurações da Aplicação
APP_DIR="/opt/taleontracker"
BACKEND_PORT="8000"
FRONTEND_PORT="3000"

# Configurações do Nginx
NGINX_SITE_CONFIG="/etc/nginx/sites-available/taleontracker"
NGINX_SITE_ENABLED="/etc/nginx/sites-enabled/taleontracker"

# Configurações do Systemd
SERVICE_NAME="taleontracker"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Versões mínimas requeridas
MIN_PYTHON_VERSION="3.8"
MIN_NODE_VERSION="14"
MIN_NPM_VERSION="6"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPO_URL="https://github.com/canetex/TaleonTracker"