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

# Verificar dependências necessárias
echo -e "${YELLOW}Verificando dependências...${NC}"
check_command git
check_command python3
check_command pip3
check_command node
check_command npm

# Configurações
INSTALL_DIR="/opt/taleontracker"
BRANCH="feature/daily-experience-tracking"

# Entrar no diretório da aplicação
cd $INSTALL_DIR

# Atualizar o código
echo -e "${YELLOW}Atualizando código...${NC}"
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

# Atualizar o banco de dados
echo -e "${YELLOW}Atualizando banco de dados...${NC}"
cd "$INSTALL_DIR/backend"
python3 init_db.py

# Atualizar dependências do backend
echo -e "${YELLOW}Atualizando dependências do backend...${NC}"
pip3 install -r requirements.txt

# Atualizar dependências do frontend
echo -e "${YELLOW}Atualizando dependências do frontend...${NC}"
cd "$INSTALL_DIR/frontend"
npm install

# Reiniciar os serviços
echo -e "${YELLOW}Reiniciando serviços...${NC}"
sudo systemctl restart taleontracker
sudo systemctl restart nginx

echo -e "${GREEN}Atualização concluída!${NC}"
echo -e "${YELLOW}Para verificar o status dos serviços, use:${NC}"
echo "sudo systemctl status taleontracker"
echo "sudo systemctl status nginx" 