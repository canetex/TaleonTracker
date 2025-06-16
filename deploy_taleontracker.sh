#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para verificar se um comando existe
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Erro: $1 não está instalado. Por favor, instale-o primeiro.${NC}"
        exit 1
    fi
}

# Função para obter o IP da máquina
get_machine_ip() {
    IP_ADDRESS=$(hostname -I | awk '{print $1}')
    echo $IP_ADDRESS
}

# Função para atualizar o IP da API no frontend
update_frontend_api_url() {
    local IP=$1
    local FRONTEND_API_FILE="$INSTALL_DIR/frontend/src/services/api.ts"
    
    echo -e "${YELLOW}Atualizando URL da API no frontend...${NC}"
    
    # Criar arquivo .env se não existir
    echo "REACT_APP_API_URL=http://$IP:8000" > "$INSTALL_DIR/frontend/.env"
    
    # Atualizar o arquivo api.ts
    sed -i "s|const baseURL = process.env.REACT_APP_API_URL || 'http://.*:8000';|const baseURL = process.env.REACT_APP_API_URL || 'http://$IP:8000';|" "$FRONTEND_API_FILE"
    
    echo -e "${GREEN}URL da API atualizada para: http://$IP:8000${NC}"
}

# Verificar dependências necessárias
echo -e "${YELLOW}Verificando dependências...${NC}"
check_command git
check_command python3
check_command pip3
check_command node
check_command npm

# Configurações
REPO_URL="https://github.com/canetex/TaleonTracker.git"
INSTALL_DIR="/opt/taleontracker"

# Obter IP da máquina
MACHINE_IP=$(get_machine_ip)

# Criar diretório de instalação se não existir
echo -e "${YELLOW}Criando diretório de instalação...${NC}"
sudo mkdir -p $INSTALL_DIR

# Clonar o repositório
echo -e "${YELLOW}Clonando repositório...${NC}"
sudo git clone $REPO_URL $INSTALL_DIR

# Dar permissões necessárias
echo -e "${YELLOW}Configurando permissões...${NC}"
sudo chown -R $USER:$USER $INSTALL_DIR
sudo chmod +x $INSTALL_DIR/*.sh

# Executar os scripts de configuração
echo -e "${YELLOW}Iniciando configuração do sistema...${NC}"
cd $INSTALL_DIR

echo -e "${GREEN}Configurando PostgreSQL...${NC}"
./setup_postgresql.sh

echo -e "${GREEN}Configurando banco de dados...${NC}"
./setup_database.sh

echo -e "${GREEN}Configurando serviço backend...${NC}"
./setup_backend_service.sh

# Atualizar URL da API no frontend
update_frontend_api_url $MACHINE_IP

# Instalar dependências do frontend
echo -e "${GREEN}Instalando dependências do frontend...${NC}"
cd "$INSTALL_DIR/frontend"
npm install
npm install axios @types/axios

echo -e "${GREEN}Configurando serviço frontend...${NC}"
cd $INSTALL_DIR
./setup_frontend_service.sh

echo -e "${GREEN}Deploy concluído!${NC}"
echo -e "${GREEN}O TaleonTracker está disponível em: http://$MACHINE_IP${NC}"
echo -e "${YELLOW}Para verificar o status dos serviços, use:${NC}"
echo "sudo systemctl status taleontracker"
echo "sudo systemctl status nginx"