# 📋 Passo a Passo - Ajustes Baseados na Documentação

## 🎯 Objetivo
Implementar ajustes na aplicação TaleonTracker conforme especificações da `DOCUMENTACAO_COMPLETA.md`.

---

## 📦 Tarefa 1: Ajustar Relacionamento Character → CharacterHistory

### 1.1. Remover Cascade Delete
**Arquivo:** `backend/models/character.py`
- **Ação:** Remover `cascade="all, delete-orphan"` do relacionamento
- **Alteração:** Mudar de `cascade="all, delete-orphan"` para `cascade="save-update"` ou remover completamente
- **Justificativa:** Personagens não devem ser deletados, e o histórico deve ser preservado mesmo se o personagem for removido (soft delete)

---

## 📦 Tarefa 2: Ajustar Lógica de daily_experience

### 2.1. Modificar Lógica no Scraper
**Arquivo:** `backend/services/scraper.py`
- **Ação:** Ajustar para que `daily_experience = 0` APENAS quando não conseguir identificar a XP do dia
- **Alteração:** 
  - Remover lógica que define `daily_experience = 0` quando não há mudança de EXP
  - Manter `daily_experience = 0` apenas quando:
    - Personagem não encontrado
    - Falha na página
    - Erro no scraping
    - Não consegue extrair valor da tabela "Experience History"
- **Localização:** Função `scrape_character_data()` (linhas ~217-260 e ~332-335)

---

## 📦 Tarefa 3: Ajustar Tratamento de Personagem Não Encontrado

### 3.1. Modificar Lógica no Scraper
**Arquivo:** `backend/services/scraper.py`
- **Ação:** Quando personagem não encontrado, manter apenas `level` e `experience` (TOTAL_EXPERIENCE) do último histórico
- **Alteração:**
  - Garantir que `daily_experience = 0` sempre
  - Manter `level` do último histórico
  - Manter `experience` (TOTAL_EXPERIENCE) do último histórico
- **Localização:** Função `scrape_character_data()` (linhas ~154-181)

---

## 📦 Tarefa 4: Criar Modelo Death e Registrar Mortes

### 4.1. Criar Modelo Death
**Arquivo:** `backend/models/death.py` (NOVO)
- **Campos:**
  - `id` (Integer, primary_key)
  - `character_name` (String)
  - `character_id` (Integer, ForeignKey para characters.id, nullable)
  - `level` (Integer)
  - `world` (String)
  - `death_date` (DateTime)
  - `timestamp` (DateTime, default=datetime.utcnow)
- **Relacionamento:** Opcional com Character (nullable)

### 4.2. Criar Serviço de Scraping de Deaths
**Arquivo:** `backend/services/death_scraper.py` (NOVO)
- **Função:** `scrape_deaths(world: str) -> List[Death]`
- **Lógica:**
  - Acessa `https://{world}.taleon.online/deaths.php`
  - Extrai informações da tabela de mortes
  - Retorna lista de mortes com: data, nome do char, level, mundo
- **Integração:** Chamar durante `discover_and_add_characters()`

### 4.3. Integrar Scraping de Deaths
**Arquivo:** `backend/services/character_discovery.py`
- **Ação:** Adicionar chamada para `scrape_deaths()` para cada mundo
- **Alteração:** Após extrair personagens, também extrair e salvar mortes

---

## 📦 Tarefa 5: Ajustar Lógica de Estatísticas e Scrapping

### 5.1. Adicionar Campo total_experience ao CharacterHistory
**Arquivo:** `backend/models/character_history.py`
- **Ação:** Adicionar coluna `total_experience` (Float, nullable)
- **Migration:** Criar migration para adicionar coluna

### 5.2. Criar Script de Limpeza de total_experience
**Arquivo:** `backend/scripts/clear_total_experience.py` (NOVO)
- **Ação:** Limpar campo `total_experience` de toda a base de dados
- **Comando SQL:** `UPDATE character_history SET total_experience = NULL;`

### 5.3. Criar Serviço de Busca de Experiência Total
**Arquivo:** `backend/services/experience_lookup.py` (NOVO)
- **Funções:**
  - `get_experience_from_highscores(character_name: str, world: str) -> float | None`
  - `get_experience_from_level_table(level: int) -> float`
- **Lógica:**
  - Primeiro tenta buscar de `https://{world}.taleon.online/highscores.php`
  - Se não encontrar, usa tabela de experiência baseada no level
  - Tabela de experiência: `https://www.tibia.com/library/?subtopic=experiencetable`

### 5.4. Ajustar Lógica de TOTAL_EXPERIENCE no Scraper
**Arquivo:** `backend/services/scraper.py`
- **Ação:** Implementar lógica de preenchimento de `total_experience`
- **Fluxo:**
  1. Se `total_experience` está NULL ou 0:
     - Busca via `get_experience_from_highscores()`
     - Se não encontrar, usa `get_experience_from_level_table(level)`
  2. A cada novo scraping:
     - `total_experience = total_experience + daily_experience`
  3. Atualiza `character_history.total_experience`

### 5.5. Ajustar Lógica de DAILY_EXPERIENCE
**Arquivo:** `backend/services/scraper.py`
- **Ação:** Permitir valores negativos e atualizar TOTAL_EXPERIENCE
- **Alteração:**
  - Remover validação que força `daily_experience >= 0`
  - Permitir valores negativos (perda de experiência por morte)
  - Após calcular `daily_experience`, atualizar `total_experience`
- **Localização:** Função `scrape_character_data()`

### 5.6. Ajustar Lógica de LEVEL com Validação
**Arquivo:** `backend/services/scraper.py`
- **Ação:** Validar TOTAL_EXPERIENCE contra tabela de experiência
- **Fluxo:**
  1. Extrai `level` do scraping
  2. Calcula experiência mínima esperada para esse level via tabela
  3. Se `total_experience < experiência_mínima_do_level`:
     - Assume que houve erro na atualização
     - Define `total_experience = experiência_mínima_do_level`
  4. Salva `level` e `total_experience` atualizados

---

## 📦 Tarefa 6: Ajustar Estatísticas AVERAGE e OVERALL

### 6.1. Modificar Cálculo de AVERAGE
**Arquivo:** `backend/routers/character_ranking.py`
- **Ação:** Reimplementar cálculo usando `total_experience`
- **Nova Lógica:**
  ```
  INITIAL_EXPERIENCE = FIRST REGISTER OF TOTAL_EXPERIENCE no intervalo
  LAST_EXPERIENCE = LAST REGISTER OF TOTAL_EXPERIENCE no intervalo
  AVERAGE = (LAST_EXPERIENCE - INITIAL_EXPERIENCE) / DAYS
  ```
- **Alteração:** Substituir lógica atual (linhas ~167-209) pela nova

### 6.2. Modificar Cálculo de OVERALL
**Arquivo:** `backend/routers/character_ranking.py`
- **Ação:** Reimplementar cálculo usando `total_experience`
- **Nova Lógica:**
  ```
  INITIAL_EXPERIENCE = FIRST REGISTER OF TOTAL_EXPERIENCE no intervalo
  LAST_EXPERIENCE = LAST REGISTER OF TOTAL_EXPERIENCE no intervalo
  OVERALL = (LAST_EXPERIENCE - INITIAL_EXPERIENCE)
  ```
- **Alteração:** Substituir lógica atual (linhas ~41-166) pela nova

### 6.3. Filtrar Personagens com Média = 0
**Arquivo:** `backend/routers/character_ranking.py`
- **Ação:** Adicionar filtro para excluir personagens com `average_experience <= 0` ou `accumulated_experience <= 0`
- **Localização:** Antes de retornar ranking (já existe parcialmente, verificar se está completo)

---

## 📦 Tarefa 7: Ajustar discover_and_add_characters

### 7.1. Adicionar Chamada para update_all_characters
**Arquivo:** `backend/services/character_discovery.py`
- **Ação:** Ao final de `discover_and_add_characters()`, chamar `update_all_characters()`
- **Alteração:** 
  - Importar `update_all_characters` de `services.scraper`
  - Chamar após adicionar novos personagens
  - Garantir que seja assíncrono

---

## 📦 Tarefa 8: Remover Schedule Automático do update_all_characters

### 8.1. Remover Agendamento
**Arquivo:** `backend/services/scheduler.py`
- **Ação:** Remover função `schedule_daily_scrape()` ou comentar sua chamada
- **Alteração:** 
  - Remover ou comentar chamada de `schedule_daily_scrape(scheduler)` em `main.py`
  - Manter apenas `schedule_character_discovery()`

---

## 📦 Tarefa 9: Adicionar Links nos Stats

### 9.1. Adicionar Link para Detalhes do Personagem
**Arquivo:** `frontend/src/pages/WorldStats.tsx`
- **Ação:** Adicionar link clicável no nome do personagem na tabela de ranking
- **Alteração:**
  - Importar `Link` do `react-router-dom`
  - Transformar nome do personagem em link para `/characters/{character_id}`
  - Localização: Tabela de ranking (linhas ~300-400)

---

## 📦 Tarefa 10: Adicionar Links no Compare

### 10.1. Adicionar Link para Detalhes do Personagem
**Arquivo:** `frontend/src/pages/CharacterCompare.tsx`
- **Ação:** Adicionar link clicável no nome do personagem
- **Alteração:**
  - Importar `Link` do `react-router-dom`
  - Transformar nome do personagem em link para `/characters/{character_id}`
  - Localização: Lista de personagens comparados

---

## 📦 Tarefa 11: Adicionar Link para Site Taleon nos Detalhes

### 11.1. Adicionar Link Externo
**Arquivo:** `frontend/src/pages/CharacterDetail.tsx`
- **Ação:** Adicionar botão/link para o site do Taleon
- **Alteração:**
  - Adicionar botão "Ver no Taleon" que abre `https://{world}.taleon.online/characterprofile.php?name={character_name}`
  - Usar `target="_blank"` para abrir em nova aba
  - Localização: Cabeçalho do personagem (próximo ao botão "Atualizar Dados")

---

## 📋 Resumo de Arquivos a Modificar

### Backend
1. ✅ `backend/models/character.py` - Remover cascade delete
2. ✅ `backend/models/character_history.py` - Adicionar total_experience
3. ✅ `backend/models/death.py` - **NOVO** - Modelo de mortes
4. ✅ `backend/services/scraper.py` - Ajustar lógicas de daily_experience, total_experience, level
5. ✅ `backend/services/character_discovery.py` - Integrar scraping de deaths e chamar update_all_characters
6. ✅ `backend/services/death_scraper.py` - **NOVO** - Scraping de mortes
7. ✅ `backend/services/experience_lookup.py` - **NOVO** - Busca de experiência total
8. ✅ `backend/services/scheduler.py` - Remover schedule de update_all_characters
9. ✅ `backend/routers/character_ranking.py` - Reimplementar cálculos AVERAGE e OVERALL
10. ✅ `backend/scripts/clear_total_experience.py` - **NOVO** - Script de limpeza
11. ✅ `backend/migrations/add_total_experience.py` - **NOVO** - Migration para total_experience
12. ✅ `backend/migrations/add_deaths_table.py` - **NOVO** - Migration para tabela deaths

### Frontend
1. ✅ `frontend/src/pages/WorldStats.tsx` - Adicionar links para detalhes
2. ✅ `frontend/src/pages/CharacterCompare.tsx` - Adicionar links para detalhes
3. ✅ `frontend/src/pages/CharacterDetail.tsx` - Adicionar link para Taleon

---

## ⚠️ Observações Importantes

1. **TOTAL_EXPERIENCE**: Campo será adicionado ao `CharacterHistory`, não ao `Character`
2. **DAILY_EXPERIENCE**: Pode ser negativo (perda por morte)
3. **LEVEL**: Sempre positivo, mas valida contra TOTAL_EXPERIENCE
4. **Deaths**: Tabela separada, relacionamento opcional com Character
5. **Schedule**: Apenas `character_discovery` será agendado, que por sua vez chama `update_all_characters()`
6. **Links**: Todos os links devem usar `react-router-dom` para navegação interna e `<a>` para externos

---

## 🧪 Testes Recomendados

1. Testar scraping com personagem existente
2. Testar scraping com personagem não encontrado
3. Testar cálculo de TOTAL_EXPERIENCE via highscores
4. Testar cálculo de TOTAL_EXPERIENCE via tabela de level
5. Testar atualização de TOTAL_EXPERIENCE com daily_experience positivo/negativo
6. Testar validação de LEVEL vs TOTAL_EXPERIENCE
7. Testar scraping de deaths
8. Testar cálculos de AVERAGE e OVERALL com nova lógica
9. Testar links no frontend (Stats, Compare, Detail)
10. Testar fluxo completo: discovery → update_all_characters

---

## 📝 Ordem de Execução Sugerida

1. **Fase 1 - Modelos e Migrations** (Tarefas 1, 4.1, 5.1)
2. **Fase 2 - Serviços Base** (Tarefas 4.2, 4.3, 5.3, 5.6)
3. **Fase 3 - Ajustes no Scraper** (Tarefas 2, 3, 5.4, 5.5)
4. **Fase 4 - Estatísticas** (Tarefa 6)
5. **Fase 5 - Integração** (Tarefas 7, 8)
6. **Fase 6 - Frontend** (Tarefas 9, 10, 11)
7. **Fase 7 - Limpeza e Testes** (Tarefa 5.2)

---

**Status:** ⏳ Aguardando Aprovação

