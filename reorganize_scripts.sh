#!/bin/bash

# Criar estrutura de diretórios
mkdir -p scripts/{install,deploy,verify,maintenance}

# Mover scripts de instalação
mv setup_postgresql.sh scripts/install/
mv setup_database.sh scripts/install/
mv setup_backend_service.sh scripts/install/
mv setup_frontend_service.sh scripts/install/
mv setup_lxc.sh scripts/install/

# Mover script de deploy
mv deploy_taleontracker.sh scripts/deploy/

# Mover scripts de verificação
mv verify_database.sh scripts/verify/
mv verify_frontend.sh scripts/verify/

# Mover script de manutenção
mv reset_database.sh scripts/maintenance/

# Atualizar permissões
chmod +x scripts/*/*.sh

# Criar arquivo de configuração
cat > scripts/config.sh << 'EOF'
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
EOF

# Criar arquivo de funções utilitárias
cat > scripts/utils.sh << 'EOF'
#!/bin/bash

# Funções de logging
log() {
    local message="$1"
    local level="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a /var/log/taleontracker/install.log
}

# Verificar se um comando existe
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log "Comando '$1' não encontrado" "ERROR"
        return 1
    fi
    return 0
}

# Verificar versão
check_version() {
    local cmd="$1"
    local min_version="$2"
    local version=$($cmd --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    
    if [ "$(printf '%s\n' "$min_version" "$version" | sort -V | head -n1)" != "$min_version" ]; then
        log "Versão do $cmd ($version) é menor que a mínima requerida ($min_version)" "ERROR"
        return 1
    fi
    return 0
}

# Verificar espaço em disco
check_disk_space() {
    local required_mb="$1"
    local available_mb=$(df -m / | awk 'NR==2 {print $4}')
    
    if [ "$available_mb" -lt "$required_mb" ]; then
        log "Espaço em disco insuficiente. Necessário: ${required_mb}MB, Disponível: ${available_mb}MB" "ERROR"
        return 1
    fi
    return 0
}

# Criar backup
create_backup() {
    local source="$1"
    local backup_dir="$2"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${backup_dir}/backup_${timestamp}.tar.gz"
    
    mkdir -p "$backup_dir"
    tar -czf "$backup_file" "$source"
    log "Backup criado: $backup_file" "INFO"
}

# Verificar permissões
check_permissions() {
    local path="$1"
    local user="$2"
    local group="$3"
    
    if [ ! -w "$path" ]; then
        log "Sem permissão de escrita em: $path" "ERROR"
        return 1
    fi
    
    if [ "$(stat -c '%U:%G' "$path")" != "$user:$group" ]; then
        log "Permissões incorretas em: $path" "ERROR"
        return 1
    fi
    
    return 0
}

# Obter IP da máquina
get_machine_ip() {
    hostname -I | awk '{print $1}'
}

# Verificar status do serviço
check_service_status() {
    local service="$1"
    if ! systemctl is-active --quiet "$service"; then
        log "Serviço $service não está rodando" "ERROR"
        return 1
    fi
    return 0
}

# Verificar uso de porta
check_port_usage() {
    local port="$1"
    if netstat -tuln | grep -q ":$port "; then
        log "Porta $port já está em uso" "ERROR"
        return 1
    fi
    return 0
}
EOF

# Criar README para cada diretório
cat > scripts/install/README.md << 'EOF'
# Scripts de Instalação

Este diretório contém os scripts necessários para a instalação do TaleonTracker.

## Scripts Disponíveis

- `setup_postgresql.sh`: Instala e configura o PostgreSQL
- `setup_database.sh`: Cria e configura o banco de dados
- `setup_backend_service.sh`: Configura o serviço do backend
- `setup_frontend_service.sh`: Configura o serviço do frontend
- `setup_lxc.sh`: Configura o ambiente LXC

## Uso

Execute os scripts na ordem correta através do script principal `setup_complete.sh`.
EOF

cat > scripts/deploy/README.md << 'EOF'
# Scripts de Deploy

Este diretório contém os scripts relacionados ao deploy do TaleonTracker.

## Scripts Disponíveis

- `deploy_taleontracker.sh`: Realiza o deploy completo da aplicação

## Uso

Execute o script de deploy após a instalação completa do sistema.
EOF

cat > scripts/verify/README.md << 'EOF'
# Scripts de Verificação

Este diretório contém os scripts para verificação do sistema.

## Scripts Disponíveis

- `verify_database.sh`: Verifica a conexão e integridade do banco de dados
- `verify_frontend.sh`: Verifica a disponibilidade do frontend

## Uso

Execute os scripts de verificação para garantir que o sistema está funcionando corretamente.
EOF

cat > scripts/maintenance/README.md << 'EOF'
# Scripts de Manutenção

Este diretório contém os scripts para manutenção do sistema.

## Scripts Disponíveis

- `reset_database.sh`: Reseta o banco de dados para o estado inicial

## Uso

Execute os scripts de manutenção quando necessário realizar tarefas de manutenção no sistema.
EOF

# Atualizar permissões
chmod +x scripts/config.sh scripts/utils.sh

echo "Reorganização concluída com sucesso!" 