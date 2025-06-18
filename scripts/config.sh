#!/bin/bash

# Configurações do banco de dados
DB_NAME="taleontracker"
DB_USER="taleon"
DB_PASS="taleon123"
DB_HOST="localhost"
DB_PORT="5432"

# Configurações do Redis
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASS="taleon123"

# Configurações da aplicação
APP_DIR="/opt/taleontracker"
BACKEND_PORT="8000"
FRONTEND_PORT="3000"

# Configurações do Nginx
NGINX_CONF="/etc/nginx/sites-available/taleontracker"
NGINX_ENABLED="/etc/nginx/sites-enabled/taleontracker"

# Configurações do Systemd
BACKEND_SERVICE="taleontracker-backend"
FRONTEND_SERVICE="taleontracker-frontend"

# Versões mínimas
MIN_PYTHON_VERSION="3.8"
MIN_NODE_VERSION="14"
MIN_NPM_VERSION="6"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
