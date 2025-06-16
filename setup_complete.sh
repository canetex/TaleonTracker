#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
    echo -e "${YELLOW}Configurando firewall...${NC}"
    
    # Verificar se o ufw está instalado
    if ! command -v ufw &> /dev/null; then
        apt install -y ufw
    fi
    
    # Configurar regras do firewall
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow 8000/tcp  # Backend API
    ufw allow 3000/tcp  # Frontend Development Server
    
    # Habilitar firewall
    ufw --force enable
    
    echo -e "${GREEN}Firewall configurado com sucesso!${NC}"
}

# Função para configurar o PostgreSQL
setup_postgresql() {
    echo -e "${YELLOW}Configurando PostgreSQL...${NC}"
    
    # Remover banco e usuário existentes
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS taleontracker;"
    sudo -u postgres psql -c "DROP ROLE IF EXISTS taleon;"
    
    # Criar usuário e banco
    sudo -u postgres psql -c "CREATE USER taleon WITH PASSWORD 'taleon123';"
    sudo -u postgres psql -c "CREATE DATABASE taleontracker OWNER taleon;"
    
    # Conceder privilégios
    sudo -u postgres psql -d taleontracker -c "GRANT ALL PRIVILEGES ON DATABASE taleontracker TO taleon;"
    sudo -u postgres psql -d taleontracker -c "GRANT ALL PRIVILEGES ON SCHEMA public TO taleon;"
    sudo -u postgres psql -d taleontracker -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO taleon;"
    sudo -u postgres psql -d taleontracker -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO taleon;"
    
    echo -e "${GREEN}PostgreSQL configurado com sucesso!${NC}"
}

# Função para verificar o status dos serviços
verify_services() {
    echo -e "${YELLOW}Verificando status dos serviços...${NC}"
    
    # Verificar PostgreSQL
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}PostgreSQL está rodando${NC}"
    else
        echo -e "${RED}PostgreSQL não está rodando${NC}"
        systemctl start postgresql
    fi
    
    # Verificar Backend
    if systemctl is-active --quiet taleontracker; then
        echo -e "${GREEN}Backend está rodando${NC}"
    else
        echo -e "${RED}Backend não está rodando${NC}"
        systemctl start taleontracker
    fi
    
    # Verificar Nginx
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}Nginx está rodando${NC}"
    else
        echo -e "${RED}Nginx não está rodando${NC}"
        systemctl start nginx
    fi
}

# Função para limpar instalação anterior
cleanup_previous_installation() {
    echo -e "${YELLOW}Limpando instalação anterior...${NC}"
    if [ -d "/opt/taleontracker" ]; then
        rm -rf /opt/taleontracker
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

# Verificar serviços
echo "📡 Verificando serviços..."
check_service "postgresql"
check_service "nginx"
check_service "redis-server"
check_service "taleontracker"

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
echo "🔴 Verificando conexão com o Redis..."
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