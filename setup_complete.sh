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