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

# Função para verificar e instalar dependências
check_and_install_dependencies() {
    log "Verificando dependências do sistema..." "INFO"
    
    local dependencies=(
        "git:git"
        "python3:python3"
        "pip3:python3-pip"
        "python3-venv:python3-venv"
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
        "python3-certbot-nginx:python3-certbot-nginx"
        "netstat:net-tools"
    )
    
    local missing_deps=()
    
    # Verificar dependências
    for dep in "${dependencies[@]}"; do
        IFS=':' read -r cmd package <<< "$dep"
        if ! command -v "$cmd" &> /dev/null; then
            log "Dependência não encontrada: $cmd" "WARNING"
            missing_deps+=("$package")
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

# Função para verificar se um comando existe
check_command() {
    local cmd=$1
    local package=$2
    
    if ! command -v $cmd &> /dev/null; then
        echo -e "${YELLOW}Instalando $cmd...${NC}"
        apt update
        
        # Casos especiais de instalação
        case $cmd in
            "pip3")
                apt install -y python3-pip
                ;;
            "node")
                apt install -y nodejs
                ;;
            "npm")
                apt install -y npm
                ;;
            *)
                if [ -n "$package" ]; then
                    apt install -y $package
                else
                    apt install -y $cmd
                fi
                ;;
        esac
        
        if command -v $cmd &> /dev/null; then
            echo -e "${GREEN}$cmd instalado com sucesso!${NC}"
        else
            echo -e "${RED}Falha ao instalar $cmd${NC}"
            return 1
        fi
    fi
    return 0
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

echo "🔍 Iniciando verificação do sistema..."

# Verificar e instalar dependências
check_and_install_dependencies || exit 1

# Verificar e iniciar serviços
verify_and_start_services || exit 1

# Verificar portas
echo "🔌 Verificando portas..."
check_port "80"    # Nginx
check_port "5432"  # PostgreSQL
check_port "8000"  # Backend
check_port "6379"  # Redis

# Verificar diretórios
echo "📁 Verificando diretórios..."
check_directory "/opt/taleontracker"
check_directory "/opt/taleontracker/backend"
check_directory "/opt/taleontracker/frontend"
check_directory "/opt/taleontracker/backend/venv"

# Verificar arquivos
echo "📄 Verificando arquivos..."
check_file "/opt/taleontracker/backend/main.py"
check_file "/opt/taleontracker/backend/requirements.txt"
check_file "/etc/nginx/sites-available/taleontracker"
check_file "/etc/systemd/system/taleontracker.service"

# Verificar comandos
echo "🔧 Verificando comandos..."
check_command "python3"
check_command "pip"
check_command "uvicorn"
check_command "redis-cli"

# Verificar conexão com o banco de dados
echo "💾 Verificando conexão com o banco de dados..."
if psql -h localhost -U postgres -d taleontracker -c "SELECT 1" &> /dev/null; then
    echo "✅ Conexão com o banco de dados OK"
else
    echo "❌ Erro na conexão com o banco de dados"
    exit 1
fi

# Verificar conexão com o Redis
echo "�� Verificando conexão com o Redis..."
if redis-cli ping &> /dev/null; then
    echo "✅ Conexão com o Redis OK"
else
    echo "❌ Erro na conexão com o Redis"
    exit 1
fi

# Verificar API
echo "🌐 Verificando API..."
if curl -s http://localhost:8000/api/health &> /dev/null; then
    echo "✅ API está respondendo"
else
    echo "❌ API não está respondendo"
    exit 1
fi

echo "✅ Verificação completa! Todos os componentes estão funcionando corretamente."

# Verificar dependências necessárias
echo -e "${YELLOW}Verificando dependências...${NC}"
check_command git || exit 1
check_command python3 || exit 1
check_command pip3 || exit 1
check_command node || exit 1
check_command npm || exit 1

# Atualizar o sistema
echo -e "${YELLOW}Atualizando o sistema...${NC}"
apt update
apt upgrade -y

# Configurar firewall
setup_firewall

# Limpar instalação anterior
cleanup_previous_installation

# Criar diretório de instalação
echo -e "${YELLOW}Criando diretório de instalação...${NC}"
mkdir -p /opt/taleontracker

# Clonar o repositório
echo -e "${YELLOW}Clonando repositório...${NC}"
git clone https://github.com/canetex/TaleonTracker.git /opt/taleontracker

# Dar permissões necessárias
echo -e "${YELLOW}Configurando permissões...${NC}"
chmod +x /opt/taleontracker/*.sh

# Navegar até o diretório
cd /opt/taleontracker

# Configurar PostgreSQL
setup_postgresql

# Executar script de configuração do LXC
echo -e "${YELLOW}Configurando ambiente LXC...${NC}"
./setup_lxc.sh

# Executar script de deploy
echo -e "${YELLOW}Iniciando deploy da aplicação...${NC}"
./deploy_taleontracker.sh

# Verificar serviços
verify_services

# Obter IP da máquina
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo -e "${GREEN}Configuração completa!${NC}"
echo -e "${GREEN}O TaleonTracker está disponível em:${NC}"
echo -e "Frontend: http://$IP_ADDRESS"
echo -e "Frontend Dev Server: http://$IP_ADDRESS:3000"
echo -e "Backend API: http://$IP_ADDRESS:8000"
echo -e "${YELLOW}Para verificar o status dos serviços:${NC}"
echo "sudo systemctl status postgresql"
echo "sudo systemctl status taleontracker"
echo "sudo systemctl status nginx"
echo -e "${YELLOW}Para verificar os logs:${NC}"
echo "sudo journalctl -u taleontracker"
echo "sudo journalctl -u nginx"

# Função para configurar arquivos de ambiente
setup_env_files() {
    log "Configurando arquivos de ambiente" "INFO"
    
    # Gerar senhas e chaves
    local db_password=$(openssl rand -base64 12)
    local redis_password=$(openssl rand -base64 12)
    local secret_key=$(openssl rand -base64 32)
    local jwt_secret=$(openssl rand -base64 32)
    
    # Configurar backend
    if [ -f "${APP_DIR}/backend/.env.template" ]; then
        cp "${APP_DIR}/backend/.env.template" "${APP_DIR}/backend/.env"
        sed -i "s/your_password_here/${db_password}/g" "${APP_DIR}/backend/.env"
        sed -i "s/your_redis_password_here/${redis_password}/g" "${APP_DIR}/backend/.env"
        sed -i "s/your_secret_key_here/${secret_key}/g" "${APP_DIR}/backend/.env"
        sed -i "s/your_jwt_secret_here/${jwt_secret}/g" "${APP_DIR}/backend/.env"
        chmod 600 "${APP_DIR}/backend/.env"
    else
        log "Template .env do backend não encontrado" "ERROR"
        return 1
    fi
    
    # Configurar frontend
    if [ -f "${APP_DIR}/frontend/.env.template" ]; then
        cp "${APP_DIR}/frontend/.env.template" "${APP_DIR}/frontend/.env"
        sed -i "s/your_api_url_here/http:\/\/localhost:${BACKEND_PORT}/g" "${APP_DIR}/frontend/.env"
        chmod 600 "${APP_DIR}/frontend/.env"
    else
        log "Template .env do frontend não encontrado" "ERROR"
        return 1
    fi
    
    # Salvar senhas em arquivo seguro
    mkdir -p /etc/taleontracker
    cat > /etc/taleontracker/.passwords << EOF
DB_PASSWORD=${db_password}
REDIS_PASSWORD=${redis_password}
SECRET_KEY=${secret_key}
JWT_SECRET=${jwt_secret}
EOF
    chmod 600 /etc/taleontracker/.passwords
    
    log "Arquivos de ambiente configurados com sucesso" "INFO"
    return 0
}

# Função para executar scripts de instalação
run_install_scripts() {
    local scripts_dir="${APP_DIR}/scripts/install"
    
    # Verificar se o diretório existe
    if [ ! -d "$scripts_dir" ]; then
        log "Diretório de scripts não encontrado: $scripts_dir" "ERROR"
        return 1
    fi
    
    # Executar scripts na ordem correta
    local scripts=(
        "setup_postgresql.sh"
        "setup_database.sh"
        "setup_backend_service.sh"
        "setup_frontend_service.sh"
        "setup_lxc.sh"
    )
    
    for script in "${scripts[@]}"; do
        local script_path="${scripts_dir}/${script}"
        if [ -f "$script_path" ]; then
            log "Executando script: $script" "INFO"
            chmod +x "$script_path"
            "$script_path" || {
                log "Falha ao executar script: $script" "ERROR"
                return 1
            }
        else
            log "Script não encontrado: $script" "ERROR"
            return 1
        fi
    done
    
    return 0
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
    
    # Configurar Nginx
    setup_nginx || exit 1
    
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
    
    # Configurar arquivos de ambiente
    setup_env_files || exit 1
    
    # Executar scripts de instalação
    run_install_scripts || exit 1
    
    # Configurar cron jobs
    setup_cron_jobs || exit 1
    
    # Configurar monitoramento
    setup_monitoring || exit 1
    
    # Executar script de deploy
    log "Iniciando deploy..." "INFO"
    "${APP_DIR}/scripts/deploy/deploy_taleontracker.sh" || {
        log "Falha no deploy" "ERROR"
        exit 1
    }
    
    # Verificar serviços novamente após o deploy
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

# Executar instalação
main 