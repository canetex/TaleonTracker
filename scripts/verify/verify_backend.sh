#!/bin/bash

# Carregar configurações e funções
source ../config.sh
source ../utils.sh

# Função para verificar o serviço do backend
check_backend_service() {
    log "Verificando serviço do backend..." "INFO"
    
    if ! systemctl is-active --quiet "$BACKEND_SERVICE"; then
        log "Serviço do backend não está rodando" "ERROR"
        return 1
    fi
    
    log "Serviço do backend está ativo" "INFO"
    return 0
}

# Função para verificar a API
check_backend_api() {
    log "Verificando API do backend..." "INFO"
    
    # Verificar se a porta está em uso
    if ! netstat -tuln | grep -q ":$BACKEND_PORT "; then
        log "Porta $BACKEND_PORT não está em uso" "ERROR"
        return 1
    fi
    
    # Testar conexão com a API
    if ! curl -s "http://localhost:$BACKEND_PORT/api/health" > /dev/null; then
        log "API não está respondendo" "ERROR"
        return 1
    fi
    
    log "API está respondendo" "INFO"
    return 0
}

# Função para verificar logs
check_backend_logs() {
    log "Verificando logs do backend..." "INFO"
    
    local log_file="/var/log/taleontracker/backend.log"
    
    if [ ! -f "$log_file" ]; then
        log "Arquivo de log não encontrado: $log_file" "ERROR"
        return 1
    fi
    
    # Verificar erros recentes
    if grep -q "ERROR" "$log_file"; then
        log "Encontrados erros nos logs" "WARNING"
        grep "ERROR" "$log_file" | tail -n 5
    else
        log "Nenhum erro encontrado nos logs" "INFO"
    fi
    
    return 0
}

# Função para verificar dependências
check_backend_dependencies() {
    log "Verificando dependências do backend..." "INFO"
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        log "Python3 não está instalado" "ERROR"
        return 1
    fi
    
    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        log "Pip3 não está instalado" "ERROR"
        return 1
    fi
    
    # Verificar virtualenv
    if ! command -v virtualenv &> /dev/null; then
        log "Virtualenv não está instalado" "ERROR"
        return 1
    fi
    
    log "Todas as dependências estão instaladas" "INFO"
    return 0
}

# Função para verificar ambiente virtual
check_virtualenv() {
    log "Verificando ambiente virtual..." "INFO"
    
    local venv_dir="${APP_DIR}/backend/venv"
    
    if [ ! -d "$venv_dir" ]; then
        log "Ambiente virtual não encontrado" "ERROR"
        return 1
    fi
    
    if [ ! -f "${venv_dir}/bin/activate" ]; then
        log "Ambiente virtual corrompido" "ERROR"
        return 1
    fi
    
    log "Ambiente virtual está correto" "INFO"
    return 0
}

# Função para verificar arquivos de configuração
check_backend_config() {
    log "Verificando arquivos de configuração..." "INFO"
    
    local config_files=(
        "${APP_DIR}/backend/.env"
        "${APP_DIR}/backend/requirements.txt"
        "${APP_DIR}/backend/config.py"
    )
    
    for file in "${config_files[@]}"; do
        if [ ! -f "$file" ]; then
            log "Arquivo de configuração não encontrado: $file" "ERROR"
            return 1
        fi
    done
    
    log "Todos os arquivos de configuração estão presentes" "INFO"
    return 0
}

# Função principal
main() {
    log "Iniciando verificação do backend" "INFO"
    
    local checks=(
        check_backend_service
        check_backend_api
        check_backend_logs
        check_backend_dependencies
        check_virtualenv
        check_backend_config
    )
    
    local failed=0
    
    for check in "${checks[@]}"; do
        if ! $check; then
            failed=$((failed + 1))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log "Verificação do backend concluída com sucesso" "INFO"
        echo -e "${GREEN}✅ Backend está funcionando corretamente${NC}"
        return 0
    else
        log "Verificação do backend falhou ($failed erros)" "ERROR"
        echo -e "${RED}❌ Backend apresenta problemas${NC}"
        return 1
    fi
}

# Executar verificação
main 