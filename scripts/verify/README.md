# Scripts de Verificação

Este diretório contém os scripts para verificação do sistema.

## Scripts Disponíveis

- `verify_database.sh`: Verifica a conexão e integridade do banco de dados
- `verify_frontend.sh`: Verifica a disponibilidade do frontend
- `verify_backend.sh`: Verifica o status do backend, incluindo:
  - Serviço do backend
  - API e endpoints
  - Logs do sistema
  - Dependências (Python, pip, virtualenv)
  - Ambiente virtual
  - Arquivos de configuração

## Uso

Execute os scripts de verificação para garantir que o sistema está funcionando corretamente:

```bash
# Verificar backend
./scripts/verify/verify_backend.sh

# Verificar banco de dados
./scripts/verify/verify_database.sh

# Verificar frontend
./scripts/verify/verify_frontend.sh
```

## Saída

Os scripts geram logs detalhados em `/var/log/taleontracker/` e exibem um resumo no terminal:

- ✅ Verde: Componente funcionando corretamente
- ❌ Vermelho: Componente com problemas
- ⚠️ Amarelo: Avisos que requerem atenção
