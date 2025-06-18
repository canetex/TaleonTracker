#!/bin/bash

# Carregar configurações e funções
source scripts/config.sh
source scripts/utils.sh

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Este script precisa ser executado como root${NC}"
    exit 1
fi

# Criar diretório de logs
mkdir -p /var/log/taleontracker

# Função para verificar se a porta do backend está disponível
check_backend_port() {
    log "Verificando disponibilidade da porta ${BACKEND_PORT}..." "INFO"
    
    if netstat -tuln | grep -q ":${BACKEND_PORT} "; then
        log "Porta ${BACKEND_PORT} já está em uso" "WARNING"
        log "Tentando identificar o processo..." "INFO"
        local pid=$(lsof -i :${BACKEND_PORT} -t)
        if [ -n "$pid" ]; then
            log "Processo usando a porta: $pid" "INFO"
            log "Tentando encerrar o processo..." "INFO"
            kill -9 $pid || {
                log "Não foi possível encerrar o processo" "ERROR"
                return 1
            }
        fi
    fi
    
    log "Porta ${BACKEND_PORT} está disponível" "INFO"
    return 0
}

# Função para verificar e instalar dependências
check_and_install_dependencies() {
    log "Verificando dependências do sistema..." "INFO"
    
    local dependencies=(
        "git:git"
        "python3:python3"
        "pip3:python3-pip"
        "dpkg -l python3-venv:python3-venv"
        "node:nodejs"
        "npm:npm"
        "nginx:nginx"
        "psql:postgresql"
        "redis-cli:redis-server"
        "curl:curl"
        "wget:wget"
        "unzip:unzip"
        "supervisord:supervisor"
        "cron:cron"
        "ufw:ufw"
        "certbot:certbot"
        "dpkg -l python3-certbot-nginx:python3-certbot-nginx"
        "netstat:net-tools"
    )
    
    local missing_deps=()
    
    # Verificar dependências
    for dep in "${dependencies[@]}"; do
        IFS=':' read -r cmd package <<< "$dep"
        if [[ $cmd == dpkg* ]]; then
            if ! dpkg -l | grep -q "^ii  $package "; then
                log "Dependência não encontrada: $package" "WARNING"
                missing_deps+=("$package")
            fi
        else
            if ! command -v "$cmd" &> /dev/null; then
                log "Dependência não encontrada: $package" "WARNING"
                missing_deps+=("$package")
            fi
        fi
    done
    
    # Se houver dependências faltantes, instalar
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log "Instalando dependências faltantes..." "INFO"
        apt update
        
        for package in "${missing_deps[@]}"; do
            log "Instalando $package..." "INFO"
            apt install -y "$package" || {
                log "Falha ao instalar $package" "ERROR"
                return 1
            }
        done
        
        # Verificar novamente após a instalação
        for dep in "${dependencies[@]}"; do
            IFS=':' read -r cmd package <<< "$dep"
            if ! command -v "$cmd" &> /dev/null; then
                log "Ainda não foi possível instalar: $package" "ERROR"
                return 1
            fi
        done
        
        log "Todas as dependências foram instaladas" "INFO"
    else
        log "Todas as dependências estão instaladas" "INFO"
    fi
    
    return 0
}

# Função para verificar e iniciar serviços
verify_and_start_services() {
    log "Verificando e iniciando serviços..." "INFO"
    
    local services=(
        "nginx"
        "postgresql"
        "redis-server"
        "supervisor"
    )
    
    local failed=0
    
    for service in "${services[@]}"; do
        if ! systemctl is-active --quiet "$service"; then
            log "Serviço $service não está rodando" "WARNING"
            log "Tentando iniciar $service..." "INFO"
            
            # Verificar se o serviço está habilitado
            if ! systemctl is-enabled --quiet "$service"; then
                log "Habilitando serviço $service..." "INFO"
                systemctl enable "$service" || {
                    log "Falha ao habilitar $service" "ERROR"
                    failed=$((failed + 1))
                    continue
                }
            fi
            
            # Tentar iniciar o serviço
            systemctl start "$service" || {
                log "Falha ao iniciar $service" "ERROR"
                failed=$((failed + 1))
            }
        else
            log "Serviço $service está rodando" "INFO"
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log "Todos os serviços estão rodando" "INFO"
        return 0
    else
        log "Alguns serviços falharam ao iniciar" "ERROR"
        return 1
    fi
}

# Função para configurar o firewall
setup_firewall() {
    log "Iniciando configuração do firewall" "INFO"
    
    if ! command -v ufw &> /dev/null; then
        apt install -y ufw
    fi
    
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow ${BACKEND_PORT}/tcp  # Backend API
    ufw allow ${FRONTEND_PORT}/tcp  # Frontend Development Server
    
    ufw --force enable
    
    log "Firewall configurado com sucesso" "INFO"
}

# Função para configurar o PostgreSQL
setup_postgresql() {
    log "Iniciando configuração do PostgreSQL" "INFO"
    
    # Gerar senha aleatória
    DB_PASSWORD=$(openssl rand -base64 12)
    
    # Remover banco e usuário existentes
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${DB_NAME};"
    sudo -u postgres psql -c "DROP ROLE IF EXISTS ${DB_USER};"
    
    # Criar usuário e banco
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';"
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
    
    # Conceder privilégios
    sudo -u postgres psql -d ${DB_NAME} -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
    sudo -u postgres psql -d ${DB_NAME} -c "GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_USER};"
    sudo -u postgres psql -d ${DB_NAME} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DB_USER};"
    sudo -u postgres psql -d ${DB_NAME} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DB_USER};"
    
    # Salvar senha em arquivo seguro
    echo "DB_PASSWORD=${DB_PASSWORD}" > /etc/taleontracker/.dbpass
    chmod 600 /etc/taleontracker/.dbpass
    
    log "PostgreSQL configurado com sucesso" "INFO"
}

# Função para verificar serviços
verify_services() {
    log "Verificando serviços..." "INFO"
    
    local services=(
        "nginx"
        "postgresql"
        "redis-server"
        "supervisor"
    )
    
    local failed=0
    
    for service in "${services[@]}"; do
        if ! systemctl is-active --quiet "$service"; then
            log "Serviço $service não está rodando" "ERROR"
            log "Tentando iniciar $service..." "INFO"
            systemctl start "$service" || {
                log "Falha ao iniciar $service" "ERROR"
                failed=$((failed + 1))
            }
        else
            log "Serviço $service está rodando" "INFO"
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log "Todos os serviços estão rodando" "INFO"
        return 0
    else
        log "Alguns serviços falharam ao iniciar" "ERROR"
        return 1
    fi
}

# Função para limpar instalação anterior
cleanup_previous_installation() {
    log "Iniciando limpeza da instalação anterior" "INFO"
    
    if [ -d "${APP_DIR}" ]; then
        # Criar backup antes de remover
        create_backup "${APP_DIR}" || {
            log "Falha ao criar backup da instalação anterior" "ERROR"
            return 1
        }
        
        rm -rf "${APP_DIR}"
    fi
}

# Função para verificar se um serviço está rodando
check_service() {
    if systemctl is-active --quiet $1; then
        echo "✅ $1 está rodando"
    else
        echo "❌ $1 não está rodando"
        exit 1
    fi
}

# Função para verificar se uma porta está em uso
check_port() {
    if netstat -tuln | grep -q ":$1 "; then
        echo "✅ Porta $1 está em uso"
    else
        echo "❌ Porta $1 não está em uso"
        exit 1
    fi
}

# Função para verificar se um diretório existe
check_directory() {
    if [ -d "$1" ]; then
        echo "✅ Diretório $1 existe"
    else
        echo "❌ Diretório $1 não existe"
        exit 1
    fi
}

# Função para verificar se um arquivo existe
check_file() {
    if [ -f "$1" ]; then
        echo "✅ Arquivo $1 existe"
    else
        echo "❌ Arquivo $1 não existe"
        exit 1
    fi
}

# Função para verificar se um comando existe
check_command() {
    if command -v $1 &> /dev/null; then
        echo "✅ Comando $1 está disponível"
    else
        echo "❌ Comando $1 não está disponível"
        exit 1
    fi
}

# Função para verificar e iniciar o backend
verify_and_start_backend() {
    log "Verificando e iniciando backend..." "INFO"
    
    # Verificar se o backend está rodando
    if ! systemctl is-active --quiet taleontracker-backend; then
        log "Backend não está rodando" "WARNING"
        log "Tentando iniciar backend..." "INFO"
        
        # Verificar se o serviço está habilitado
        if ! systemctl is-enabled --quiet taleontracker-backend; then
            log "Habilitando serviço taleontracker-backend..." "INFO"
            systemctl enable taleontracker-backend || {
                log "Falha ao habilitar serviço taleontracker-backend" "ERROR"
                return 1
            }
        fi
        
        # Tentar iniciar o serviço
        systemctl start taleontracker-backend || {
            log "Falha ao iniciar backend" "ERROR"
            return 1
        }
    else
        log "Backend está rodando" "INFO"
    fi
    
    return 0
}

# Função para configurar o backend
setup_backend() {
    log "Configurando backend..." "INFO"
    
    # Criar e ativar ambiente virtual
    cd "${APP_DIR}/backend"
    python3 -m venv venv
    source venv/bin/activate
    
    # Instalar dependências
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Configurar variáveis de ambiente
    if [ ! -f .env ]; then
        cp .env.template .env
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/" .env
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=${REDIS_PASSWORD}/" .env
    fi
    
    # Configurar serviço systemd
    cat > /etc/systemd/system/taleontracker-backend.service << EOF
[Unit]
Description=TaleonTracker Backend
After=network.target postgresql.service redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}/backend
Environment="PATH=${APP_DIR}/backend/venv/bin"
ExecStart=${APP_DIR}/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT}
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    # Recarregar systemd e iniciar serviço
    systemctl daemon-reload
    systemctl enable taleontracker-backend
    systemctl start taleontracker-backend
    
    log "Backend configurado com sucesso" "INFO"
}

# Função para configurar o frontend
setup_frontend() {
    log "Configurando frontend..." "INFO"
    
    # Instalar dependências
    cd "${APP_DIR}/frontend"
    npm install
    
    # Configurar variáveis de ambiente
    if [ ! -f .env ]; then
        cp .env.template .env
        sed -i "s/VITE_API_URL=.*/VITE_API_URL=http:\/\/localhost:${BACKEND_PORT}/" .env
    fi
    
    # Configurar serviço systemd
    cat > /etc/systemd/system/taleontracker-frontend.service << EOF
[Unit]
Description=TaleonTracker Frontend
After=network.target taleontracker-backend.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}/frontend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/npm run dev
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    # Recarregar systemd e iniciar serviço
    systemctl daemon-reload
    systemctl enable taleontracker-frontend
    systemctl start taleontracker-frontend
    
    log "Frontend configurado com sucesso" "INFO"
}

# Função para configurar o Nginx
setup_nginx() {
    log "Configurando Nginx..." "INFO"
    
    # Criar configuração do Nginx
    cat > /etc/nginx/sites-available/taleontracker << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:${FRONTEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:${BACKEND_PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
    
    # Habilitar site e reiniciar Nginx
    ln -sf /etc/nginx/sites-available/taleontracker /etc/nginx/sites-enabled/
    nginx -t && systemctl restart nginx
    
    log "Nginx configurado com sucesso" "INFO"
}

# Função principal de instalação
main() {
    log "Iniciando instalação do TaleonTracker" "INFO"
    
    # Verificar espaço em disco (mínimo 1GB)
    check_disk_space 1024 || {
        log "Espaço em disco insuficiente" "ERROR"
        exit 1
    }
    
    # Verificar e instalar dependências
    check_and_install_dependencies || exit 1
    
    # Verificar e iniciar serviços
    verify_and_start_services || exit 1
    
    # Configurar firewall
    setup_firewall || exit 1
    
    # Configurar PostgreSQL
    setup_postgresql || exit 1
    
    # Configurar Redis
    setup_redis || exit 1
    
    # Criar diretório da aplicação
    mkdir -p "${APP_DIR}"
    chown -R www-data:www-data "${APP_DIR}"
    
    # Clonar o repositório
    log "Clonando repositório..." "INFO"
    git clone https://github.com/canetex/TaleonTracker.git "${APP_DIR}" || {
        log "Falha ao clonar repositório" "ERROR"
        exit 1
    }
    
    # Configurar backend
    setup_backend || exit 1
    
    # Configurar frontend
    setup_frontend || exit 1
    
    # Configurar Nginx
    setup_nginx || exit 1
    
    # Configurar cron jobs
    setup_cron_jobs || exit 1
    
    # Configurar monitoramento
    setup_monitoring || exit 1
    
    # Verificar serviços novamente
    verify_and_start_services || exit 1
    
    log "Instalação concluída com sucesso" "INFO"
    
    # Mostrar informações de acesso
    IP_ADDRESS=$(get_machine_ip)
    echo -e "${GREEN}Configuração completa!${NC}"
    echo -e "${GREEN}O TaleonTracker está disponível em:${NC}"
    echo -e "Frontend: http://$IP_ADDRESS"
    echo -e "Frontend Dev Server: http://$IP_ADDRESS:${FRONTEND_PORT}"
    echo -e "Backend API: http://$IP_ADDRESS:${BACKEND_PORT}"
    
    # Mostrar comandos úteis
    echo -e "${YELLOW}Comandos úteis:${NC}"
    echo "Verificar status: ./scripts/verify/verify_database.sh"
    echo "Verificar frontend: ./scripts/verify/verify_frontend.sh"
    echo "Verificar backend: ./scripts/verify/verify_backend.sh"
    echo "Resetar banco: ./scripts/maintenance/reset_database.sh"
    
    # Mostrar informações de monitoramento
    echo -e "${YELLOW}Monitoramento:${NC}"
    echo "Logs: /var/log/taleontracker/"
    echo "Backups: /var/backups/taleontracker/"
    echo "Status dos serviços: supervisorctl status"
}

# Executar função principal
main 