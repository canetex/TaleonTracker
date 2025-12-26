#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Teste no Servidor - TaleonTracker ===${NC}"

# Verificar se docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Erro: docker-compose não está instalado${NC}"
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Erro: docker-compose.yml não encontrado. Execute este script na raiz do projeto.${NC}"
    exit 1
fi

# Parar containers existentes
echo -e "\n${YELLOW}Parando containers existentes...${NC}"
docker-compose down

# Reconstruir containers
echo -e "\n${YELLOW}Reconstruindo containers...${NC}"
docker-compose build --no-cache

# Iniciar containers
echo -e "\n${YELLOW}Iniciando containers...${NC}"
docker-compose up -d

# Aguardar alguns segundos para os serviços iniciarem
echo -e "\n${YELLOW}Aguardando serviços iniciarem...${NC}"
sleep 10

# Verificar status dos containers
echo -e "\n${YELLOW}Verificando status dos containers...${NC}"
docker-compose ps

# Verificar logs
echo -e "\n${YELLOW}Últimas linhas dos logs do backend:${NC}"
docker-compose logs --tail=20 backend

echo -e "\n${YELLOW}Últimas linhas dos logs do frontend:${NC}"
docker-compose logs --tail=20 frontend

# Verificar se as portas estão acessíveis
echo -e "\n${YELLOW}Verificando portas...${NC}"
if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    echo -e "${GREEN}✓ Backend está rodando na porta 8000${NC}"
else
    echo -e "${RED}✗ Backend não está acessível na porta 8000${NC}"
fi

if netstat -tuln 2>/dev/null | grep -q ":3000 "; then
    echo -e "${GREEN}✓ Frontend está rodando na porta 3000${NC}"
else
    echo -e "${RED}✗ Frontend não está acessível na porta 3000${NC}"
fi

# Obter IP da máquina
IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo -e "\n${GREEN}=== Informações de Acesso ===${NC}"
echo -e "IP da máquina: $IP_ADDRESS"
echo -e "Frontend: http://$IP_ADDRESS:3000"
echo -e "Backend API: http://$IP_ADDRESS:8000"
echo -e "API Health: http://$IP_ADDRESS:8000/health"

echo -e "\n${GREEN}=== Teste concluído ===${NC}"
echo -e "${YELLOW}Para ver os logs em tempo real, execute:${NC}"
echo -e "docker-compose logs -f"

echo -e "\n${YELLOW}Para parar os containers, execute:${NC}"
echo -e "docker-compose down"

