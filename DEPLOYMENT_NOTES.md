# Notas de Deploy - Alterações Profundas

## Alterações Implementadas

### 1. Layout 80% de Largura ✅
- Ajustado o layout principal para ocupar 80% da largura da tela (máximo 1400px)
- Arquivo: `frontend/src/App.tsx`

### 2. Filtros/Buscas de Personagens ✅
- Implementados filtros de busca por nome/vocação e por mundo
- Arquivo: `frontend/src/pages/CharacterList.tsx`
- Complexidade: O(n) onde n é o número de personagens

### 3. Desativação do Mundo Gaia ✅
- Mundo Gaia removido das configurações do servidor Taleon
- Arquivo: `backend/services/scraper.py`
- Apenas San e Aura estão disponíveis

### 4. Opt-in/out de Cookies ✅
- Componente de consentimento de cookies implementado
- Arquivo: `frontend/src/components/CookieConsent.tsx`
- Persistência no localStorage

### 5. Histórico Gráfico de EXP Total do Servidor/Mundo ✅
- Nova página de estatísticas com gráfico de EXP Total
- Arquivo: `frontend/src/pages/WorldStats.tsx`
- Backend: `backend/routers/server_stats.py`

### 6. Histórico Gráfico de Ativos do Servidor/Mundo ✅
- Gráfico de personagens ativos por mundo
- Mesma página de estatísticas
- Backend: `backend/routers/server_stats.py`

## Migração do Banco de Dados

### Nova Tabela: server_stats
Execute o script de migração antes de fazer deploy:

```bash
cd backend
python migrations/add_server_stats_table.py
```

Este script:
- Cria a tabela `server_stats` sem afetar dados existentes
- Adiciona índices para melhor performance
- É idempotente (pode ser executado múltiplas vezes)

## Arquivos Modificados

### Backend
- `backend/models/server_stats.py` (novo)
- `backend/schemas/server_stats.py` (novo)
- `backend/routers/server_stats.py` (novo)
- `backend/routers/characters.py` (modificado)
- `backend/services/scraper.py` (modificado)
- `backend/main.py` (modificado)
- `backend/models/__init__.py` (modificado)
- `backend/init_db.py` (modificado)
- `backend/migrations/add_server_stats_table.py` (novo)

### Frontend
- `frontend/src/App.tsx` (modificado)
- `frontend/src/pages/CharacterList.tsx` (modificado)
- `frontend/src/pages/WorldStats.tsx` (novo)
- `frontend/src/components/CookieConsent.tsx` (novo)
- `frontend/src/components/Navbar.tsx` (modificado)
- `frontend/src/services/api.ts` (modificado)

## Comandos de Deploy

### 1. Backup do Banco de Dados (OBRIGATÓRIO)
```bash
# No servidor remoto
ssh root@217.196.63.249
cd /opt/tibia-tracker
pg_dump -U taleon taleontracker > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Atualizar Código
```bash
# No servidor remoto
cd /opt/tibia-tracker
git pull origin feature/major-updates
```

### 3. Executar Migração
```bash
cd /opt/tibia-tracker/Backend
python3 migrations/add_server_stats_table.py
```

### 4. Recompilar Containers
```bash
cd /opt/tibia-tracker
docker-compose down
docker-compose build
docker-compose up -d
```

### 5. Verificar Serviços
```bash
docker-compose ps
docker-compose logs -f backend
```

## Testes

Execute os testes após o deploy:

```bash
cd backend
pytest tests/
```

## Notas Importantes

⚠️ **NUNCA LIMPE OS DADOS DO BANCO DE DADOS**
- Todos os scripts de migração preservam dados existentes
- Sempre faça backup antes de executar migrações
- O script de migração é idempotente e seguro

## Funcionalidades Novas

### Página de Estatísticas
- Acesse em: `/stats`
- Permite visualizar gráficos de EXP Total e Personagens Ativos por mundo
- Requer cálculo prévio das estatísticas via API: `POST /api/stats/worlds/{world}/calculate-stats`

### Filtros de Busca
- Busca por nome ou vocação
- Filtro por mundo
- Funciona em tempo real enquanto digita

### Cookies
- Banner de consentimento aparece na primeira visita
- Usuário pode aceitar ou rejeitar
- Botão para gerenciar cookies aparece se rejeitado

