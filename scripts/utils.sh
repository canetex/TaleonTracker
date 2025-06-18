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
