#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Teste de Instalação do TaleonTracker ===${NC}"

# Verificar se os serviços estão rodando
echo -e "\n${YELLOW}Verificando serviços...${NC}"
services=("nginx" "postgresql" "redis-server" "taleontracker-backend" "taleontracker-frontend")

for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✓ $service está rodando${NC}"
    else
        echo -e "${RED}✗ $service não está rodando${NC}"
    fi
done

# Verificar se as portas estão abertas
echo -e "\n${YELLOW}Verificando portas...${NC}"
ports=("80" "3000" "8000" "5432" "6379")

for port in "${ports[@]}"; do
    if netstat -tuln | grep -q ":$port "; then
        echo -e "${GREEN}✓ Porta $port está aberta${NC}"
    else
        echo -e "${RED}✗ Porta $port não está aberta${NC}"
    fi
done

# Verificar se os arquivos .env foram criados
echo -e "\n${YELLOW}Verificando arquivos de configuração...${NC}"
if [ -f "/opt/taleontracker/backend/.env" ]; then
    echo -e "${GREEN}✓ Backend .env existe${NC}"
else
    echo -e "${RED}✗ Backend .env não existe${NC}"
fi

if [ -f "/opt/taleontracker/frontend/.env" ]; then
    echo -e "${GREEN}✓ Frontend .env existe${NC}"
else
    echo -e "${RED}✗ Frontend .env não existe${NC}"
fi

# Verificar se os diretórios foram criados
echo -e "\n${YELLOW}Verificando diretórios...${NC}"
directories=("/opt/taleontracker" "/var/log/taleontracker" "/var/backups/taleontracker" "/etc/taleontracker")

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ Diretório $dir existe${NC}"
    else
        echo -e "${RED}✗ Diretório $dir não existe${NC}"
    fi
done

# Mostrar IP da máquina
IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo -e "\n${YELLOW}Informações de acesso:${NC}"
echo -e "IP da máquina: $IP_ADDRESS"
echo -e "Frontend: http://$IP_ADDRESS"
echo -e "Frontend Dev Server: http://$IP_ADDRESS:3000"
echo -e "Backend API: http://$IP_ADDRESS:8000"

echo -e "\n${GREEN}=== Teste concluído ===${NC}" 