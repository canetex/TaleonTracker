#!/bin/bash

# Função para log
log() {
    local message=$1
    local level=${2:-"INFO"}
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> /var/log/taleontracker/install.log
}

# Função para verificar se um comando existe
check_command() {
    local cmd=$1
    local package=$2
    
    if ! command -v $cmd &> /dev/null; then
        log "Instalando $cmd..." "INFO"
        apt update
        
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
            log "$cmd instalado com sucesso!" "INFO"
        else
            log "Falha ao instalar $cmd" "ERROR"
            return 1
        fi
    fi
    return 0
}

# Função para verificar versão
check_version() {
    local cmd=$1
    local min_version=$2
    local current_version
    
    if ! command -v $cmd &> /dev/null; then
        log "$cmd não está instalado" "ERROR"
        return 1
    fi
    
    case $cmd in
        "python3")
            current_version=$(python3 --version | cut -d' ' -f2)
            ;;
        "node")
            current_version=$(node --version | cut -d'v' -f2)
            ;;
        "npm")
            current_version=$(npm --version)
            ;;
        *)
            log "Verificação de versão não implementada para $cmd" "ERROR"
            return 1
            ;;
    esac
    
    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" = "$min_version" ]; then
        log "Versão do $cmd ($current_version) é compatível" "INFO"
        return 0
    else
        log "Versão do $cmd ($current_version) é menor que a mínima requerida ($min_version)" "ERROR"
        return 1
    fi
}

# Função para verificar espaço em disco
check_disk_space() {
    local required_space=$1  # em MB
    local available_space=$(df -m / | awk 'NR==2 {print $4}')
    
    if [ "$available_space" -lt "$required_space" ]; then
        log "Espaço em disco insuficiente. Necessário: ${required_space}MB, Disponível: ${available_space}MB" "ERROR"
        return 1
    fi
    return 0
}

# Função para criar backup
create_backup() {
    local source=$1
    local backup_dir="/var/backups/taleontracker"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/backup_${timestamp}.tar.gz"
    
    mkdir -p "$backup_dir"
    
    if tar -czf "$backup_file" -C "$(dirname "$source")" "$(basename "$source")"; then
        log "Backup criado com sucesso: $backup_file" "INFO"
        return 0
    else
        log "Falha ao criar backup" "ERROR"
        return 1
    fi
}

# Função para verificar permissões
check_permissions() {
    local dir=$1
    local user=$2
    
    if [ ! -w "$dir" ]; then
        log "Sem permissão de escrita em $dir" "ERROR"
        return 1
    fi
    
    if [ -n "$user" ] && [ "$(stat -c '%U' "$dir")" != "$user" ]; then
        log "Diretório $dir não pertence ao usuário $user" "ERROR"
        return 1
    fi
    
    return 0
}
