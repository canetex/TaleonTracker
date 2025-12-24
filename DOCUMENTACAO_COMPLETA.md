# 📚 Documentação Completa - TaleonTracker

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Modelos de Dados e Relacionamentos](#modelos-de-dados-e-relacionamentos)
4. [Processamentos de Dados](#processamentos-de-dados)
5. [Funcionalidades da Aplicação](#funcionalidades-da-aplicação)
6. [Fluxos de Dados](#fluxos-de-dados)
7. [Tarefas Agendadas](#tarefas-agendadas)
8. [APIs e Endpoints](#apis-e-endpoints)
9. [Interface do Usuário](#interface-do-usuário)

---

## 🎯 Visão Geral

O **TaleonTracker** é uma aplicação web completa para monitoramento e análise de personagens do jogo **Taleon Online**. O sistema realiza scraping automático de dados dos servidores San e Aura, armazena histórico de evolução e apresenta visualizações interativas através de gráficos e rankings.

### Objetivos Principais

- **Monitoramento Automático**: Coleta diária de dados de personagens via web scraping
- **Histórico Completo**: Armazenamento de evolução ao longo do tempo (nível, experiência, mortes)
- **Análise e Visualização**: Gráficos interativos, rankings e comparações
- **Descoberta Automática**: Identificação e inclusão de novos personagens de rankings e mortes

---

## 🏗️ Arquitetura do Sistema

### Stack Tecnológica

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)            │
│  - Material-UI (MUI)                                        │
│  - Chart.js (Gráficos)                                      │
│  - React Router (Navegação)                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│                    Caddy (Reverse Proxy)                     │
│  - Roteamento /api → Backend                                │
│  - Roteamento / → Frontend                                  │
│  - SSL/TLS (HTTPS)                                          │
└──────────────┬───────────────────────┬──────────────────────┘
               │                       │
    ┌──────────▼──────────┐  ┌─────────▼──────────┐
    │  Backend (FastAPI)  │  │  Frontend (React)  │
    │  - Python 3.9       │  │  - Node.js         │
    │  - FastAPI          │  │  - Port 3000       │
    │  - Port 8000       │  │                    │
    └──────────┬──────────┘  └────────────────────┘
               │
    ┌──────────▼──────────────────────────────────┐
    │         PostgreSQL (Database)               │
    │  - Personagens                              │
    │  - Histórico                                │
    │  - Estatísticas do Servidor                 │
    │  - Favoritos                                │
    └─────────────────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │   Redis (Cache)      │
    │  - Cache de HTML     │
    │  - Cache de API      │
    └──────────────────────┘
```

### Componentes Principais

1. **Frontend (React)**: Interface do usuário com Material-UI
2. **Backend (FastAPI)**: API REST com processamento assíncrono
3. **Caddy**: Reverse proxy e servidor web
4. **PostgreSQL**: Banco de dados relacional
5. **Redis**: Cache para otimização de performance
6. **Docker**: Containerização de todos os serviços

---

## 📊 Modelos de Dados e Relacionamentos

### Estrutura do Banco de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                    CHARACTERS                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ id (PK)                                               │  │
│  │ name (UNIQUE, INDEXED)                                │  │
│  │ level                                                  │  │
│  │ vocation                                               │  │
│  │ world (san/aura)                                       │  │
│  │ guild                                                  │  │
│  │ outfit (caminho local)                                  │  │
│  │ created_at                                             │  │
│  │ updated_at                                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                   │
│                          │ 1:N                               │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            CHARACTER_HISTORY                          │  │
│  │  id (PK)                                              │  │
│  │  character_id (FK → characters.id)                    │  │
│  │  level                                                 │  │
│  │  experience                                            │  │
│  │  daily_experience                                      │  │
│  │  deaths                                                │  │
│  │  timestamp                                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            SERVER_STATS                                │  │
│  │  id (PK)                                               │  │
│  │  world (san/aura)                                      │  │
│  │  total_experience                                      │  │
│  │  active_characters                                     │  │
│  │  timestamp                                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            CHARACTER_FAVORITES                        │  │
│  │  id (PK)                                               │  │
│  │  character_id (FK → characters.id)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Relacionamentos

1. **Character → CharacterHistory** (1:N)
   - Um personagem tem múltiplos registros de histórico
   - Cada registro representa um snapshot em um momento específico
   - Relacionamento com `cascade="all, delete-orphan"` (deleta histórico ao deletar personagem)

2. **Character → CharacterFavorite** (1:N)
   - Um personagem pode ser favoritado por múltiplos usuários (futuro)
   - Atualmente: relação simples 1:1 (um favorito por personagem)

3. **ServerStats** (Independente)
   - Agregações por mundo e data
   - Não tem FK direto, mas relaciona-se logicamente com Character através do campo `world`

---

## ⚙️ Processamentos de Dados

### 1. Web Scraping de Personagens (`services/scraper.py`)

#### Fluxo de Processamento

```
┌─────────────────────────────────────────────────────────────┐
│ 1. REQUISIÇÃO HTTP                                          │
│    - URL: https://{world}.taleon.online/characterprofile.php│
│    - Headers: User-Agent, Accept, etc.                      │
│    - Timeout: 20s conexão, 25s total                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 2. PARSE HTML (BeautifulSoup)                              │
│    - Detecta se personagem existe                           │
│    - Extrai tabela de informações                          │
│    - Valida estrutura da página                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 3. EXTRAÇÃO DE DADOS                                       │
│    ✓ Nome (formatado)                                      │
│    ✓ Nível (remove formatação)                            │
│    ✓ Vocação                                               │
│    ✓ Mundo (detectado pela URL)                            │
│    ✓ Guild (link ou texto)                                 │
│    ✓ Experiência Total                                     │
│    ✓ Mortes                                                │
│    ✓ Experiência Diária (tabela "Experience History")     │
│    ✓ Outfit (URL da imagem)                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 4. DOWNLOAD DE OUTFIT                                      │
│    - Baixa imagem do servidor Taleon                       │
│    - Salva em /app/static/outfits/                         │
│    - Nome: {character_id}_{world}_{filename}               │
│    - Retorna caminho: /api/static/outfits/{filename}      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ 5. PERSISTÊNCIA NO BANCO                                   │
│    - Atualiza tabela CHARACTERS                            │
│    - Cria registro em CHARACTER_HISTORY                     │
│    - Verifica duplicatas (mesmo dia)                       │
│    - Se não há mudança de EXP: daily_experience = 0         │
└─────────────────────────────────────────────────────────────┘
```

#### Tratamento de Erros

- **Personagem não encontrado**: Cria registro com `daily_experience=0`, mantém level/exp do último histórico
- **Timeout**: Retorna `False`, loga erro, continua com próximo personagem
- **HTML inválido**: Valida estrutura, retorna `False` se não encontrar dados

#### Cache

- **Redis**: Cache de HTML por 5 minutos (300s)
- **Evita requisições duplicadas** em curto período
- **Pode ser desabilitado** com `use_cache=False` para dados frescos

### 2. Descoberta Automática de Personagens (`services/character_discovery.py`)

#### Fontes de Dados

```
┌─────────────────────────────────────────────────────────────┐
│  POWERGAMERS (Top Players)                                 │
│  ├─ https://aura.taleon.online/powergamers.php             │
│  └─ https://san.taleon.online/powergamers.php               │
│                                                              │
│  DEATHS (Últimas Mortes)                                    │
│  ├─ https://aura.taleon.online/deaths.php                   │
│  └─ https://san.taleon.online/deaths.php                    │
└─────────────────────────────────────────────────────────────┘
```

#### Processamento

1. **Extração de HTML**: Requisições assíncronas para cada URL
2. **Parse de Tabelas**: Identifica links `characterprofile.php?name=...`
3. **Extração de Nomes**: Decodifica URL encoding, valida formato
4. **Detecção de Mundo**: Identifica mundo pela URL de origem
5. **Inserção no Banco**: 
   - Verifica se já existe (evita duplicatas)
   - Cria registro com `level=0`, `vocation=""` (será preenchido no próximo scraping)
   - Associa ao mundo correto (san/aura)

#### Complexidade

- **O(n)**: Onde n é o número de personagens encontrados nas páginas
- **Execução**: Assíncrona, processa todas as fontes em paralelo

### 3. Preenchimento de Dias Faltantes (`services/fill_missing_days.py`)

#### Objetivo

Garantir que gráficos tenham dados contínuos, preenchendo lacunas com valores apropriados.

#### Lógica de Preenchimento

```
Para cada dia no período:
  Se existe registro real (id > 0):
    ✓ Usa valores reais
    ✓ Atualiza last_level e last_experience
  Senão:
    ✓ Cria registro preenchido (id = 0)
    ✓ level = last_level (mantém do dia anterior)
    ✓ experience = 0 (sempre 0 quando não há dados)
    ✓ daily_experience = 0
    ✓ deaths = 0
```

#### Aplicação

- **Server Stats**: Preenche `server_stats` para gráficos de mundo
- **Character History**: Preenche histórico de personagens para gráficos individuais
- **Limite**: Preenche apenas até a última data com registro real (não cria registros futuros)

### 4. Cálculo de Estatísticas Agregadas (`routers/server_stats.py`)

#### Experiência Total do Mundo

```
Para cada data no período:
  1. Busca experiência mais recente de cada personagem até aquela data
  2. Soma todas as experiências
  3. Conta personagens únicos (ativos)
  4. Armazena em SERVER_STATS
```

#### Personagens Ativos

- **Definição**: Personagem com registro de histórico até a data
- **Cálculo**: `COUNT(DISTINCT character_id)` agrupado por data

### 5. Cálculo de Rankings (`routers/character_ranking.py`)

#### Tipo: Acumulada

```
Experiência Acumulada = MAX(exp no período) - MAX(exp antes do período)

Para cada personagem:
  1. Busca MAX(experience) no período
  2. Busca MAX(experience) ANTES do período
  3. Calcula diferença
  4. Filtra apenas valores > 0
  5. Ordena decrescente
```

#### Tipo: Média Diária

```
Experiência Média = (ÚLTIMA_EXP - PRIMEIRA_EXP) / INTERVALO_DIAS

Para cada personagem:
  1. Busca MIN(experience) e MAX(experience) no período
  2. Calcula diferença total
  3. Divide pelo número de dias do intervalo
  4. Filtra apenas valores > 0
  5. Ordena decrescente
  6. Arredonda para cima (Math.ceil)
```

---

## 🎨 Funcionalidades da Aplicação

### Backend (API REST)

#### 1. Gerenciamento de Personagens (`/api/characters`)

**Endpoints:**

- `GET /api/characters` - Lista todos os personagens
  - Retorna: Array de personagens com dados enriquecidos do histórico
  - Inclui: level, experience, daily_experience, last_updated, history

- `GET /api/characters/{id}` - Detalhes de um personagem
  - Parâmetros: `days` (filtro de período, 0 = todos)
  - Retorna: Personagem completo com histórico filtrado
  - **Preenche dias faltantes** até última data real

- `POST /api/characters` - Criar novo personagem
  - Body: `{name: string, world: string}`
  - Ação: Cria registro e executa scraping inicial

- `POST /api/characters/{id}/update` - Atualizar personagem manualmente
  - Ação: Executa scraping com `use_cache=True`

- `POST /api/characters/update-all` - Atualizar todos os personagens
  - Ação: Executa scraping completo em background
  - Retorna: Mensagem de confirmação (não bloqueia)

- `POST /api/characters/discover` - Descobrir novos personagens
  - Ação: Executa descoberta automática
  - Retorna: Estatísticas (total encontrados, adicionados, existentes, erros)

- `DELETE /api/characters/{id}` - Deletar personagem
  - Ação: Remove personagem e todo seu histórico (cascade)

#### 2. Estatísticas do Servidor (`/api/stats`)

**Endpoints:**

- `GET /api/stats/worlds` - Lista mundos disponíveis
  - Retorna: `["san", "aura"]`

- `GET /api/stats/worlds/{world}/exp-history?days={N}` - Histórico de EXP total
  - Parâmetros: `days` (padrão: 30, 0 = todos)
  - Retorna: Array de `ServerStats` com `total_experience` por data
  - **Preenche dias faltantes** até hoje

- `GET /api/stats/worlds/{world}/active-history?days={N}` - Histórico de personagens ativos
  - Parâmetros: `days` (padrão: 30, 0 = todos)
  - Retorna: Array de `ServerStats` com `active_characters` por data
  - **Preenche dias faltantes** até hoje

- `POST /api/stats/worlds/{world}/calculate-stats` - Calcular estatísticas manualmente
  - Ação: Calcula e salva estatísticas agregadas para o mundo

- `POST /api/stats/worlds/{world}/fill-missing-days?days={N}` - Preencher dias faltantes
  - Parâmetros: `days` (padrão: 90)
  - Ação: Preenche `server_stats` com valores do dia anterior

#### 3. Ranking de Experiência (`/api/ranking/experience`)

**Parâmetros:**

- `days` (padrão: 30) - Período para cálculo
- `limit` (padrão: 100) - Número máximo de resultados
- `world` (opcional) - Filtrar por mundo (san/aura)
- `type` (padrão: "accumulated") - Tipo de ranking:
  - `"accumulated"`: Experiência acumulada no período
  - `"average"`: Experiência média diária no período

**Retorna:**

```json
[
  {
    "rank": 1,
    "character_id": 123,
    "name": "Character Name",
    "world": "san",
    "vocation": "Royal Paladin",
    "guild": "Guild Name",
    "level": 1427,
    "accumulated_experience": 500000000,  // ou average_experience
    "max_experience": 500000000,
    "last_update": "2025-12-24T00:00:00"
  }
]
```

**Filtros:**

- Remove personagens com experiência = 0
- Ordena decrescente por experiência
- Arredonda valores para cima (inteiros)

#### 4. Favoritos (`/api/favorites`)

**Endpoints:**

- `GET /api/favorites` - Lista favoritos do usuário
- `POST /api/favorites/{character_id}` - Adicionar favorito
- `DELETE /api/favorites/{character_id}` - Remover favorito

### Frontend (React)

#### 1. Página: Lista de Personagens (`/characters`)

**Funcionalidades:**

- **Listagem**: Grid responsivo com cards de personagens
- **Estatísticas Gerais**: 
  - Total de personagens
  - Nível médio
  - EXP nas últimas 24hs (soma total)
- **Filtros**:
  - Busca por nome ou vocação
  - Filtro por mundo
  - Filtro por guild
  - Checkbox "Apenas Favoritos"
  - Select "Chars com EXP nos últimos dias" (1, 3, 7, 15, 30, 60, 90 dias)
- **Ações**:
  - Favoritar/Desfavoritar (ícone estrela)
  - Ver detalhes (botão "Detalhes")
- **Campos Exibidos**:
  - Outfit (imagem)
  - Nome
  - Nível
  - Vocação
  - Mundo
  - Guild
  - Experiência nas últimas 24hs
  - Última atualização

**Lógica de Filtros:**

```typescript
Filtro "Chars com EXP nos últimos dias":
  1. Verifica se last_updated está no período E daily_experience > 0
  2. OU verifica histórico para encontrar ganho de experiência no período
  3. Considera mudança de experiência entre registros consecutivos
```

#### 2. Página: Detalhes do Personagem (`/characters/:id`)

**Funcionalidades:**

- **Informações Principais**:
  - Outfit, Nome, Nível, Experiência Total, EXP nas últimas 24hs
- **Gráfico de Progresso**:
  - Linha dupla: Nível (eixo Y esquerdo) e Experiência (eixo Y direito)
  - Linha pontilhada: Média diária de EXP (se calculável)
  - Filtro de período: 7, 15, 30, 45, 90, 180 dias, Todos
- **Preenchimento Automático**:
  - Preenche dias faltantes até última data real
  - Experiência = 0 para dias sem dados
  - Level mantém do último registro conhecido

**Cálculo de Média Diária:**

```typescript
Se history.length > 1:
  firstExp = history[0].experience
  lastExp = history[history.length - 1].experience
  daysDiff = diferença em dias entre primeiro e último
  averageDailyExp = (lastExp - firstExp) / daysDiff
```

#### 3. Página: Comparação (`/characters/compare`)

**Funcionalidades:**

- **Seleção**: Até 5 personagens para comparar
- **Tabela Comparativa**:
  - Nome, Nível, Experiência, EXP nas últimas 24hs, Vocação, Mundo, Guild
  - Destaque visual para diferenças
- **Gráfico Comparativo**:
  - Linha para cada personagem (cores diferentes)
  - Últimos 30 registros de cada um
  - Eixo X: Datas, Eixo Y: Experiência

#### 4. Página: Estatísticas do Servidor (`/stats`)

**Funcionalidades:**

- **Seleção de Mundo**: Dropdown (San/Aura)
- **Gráfico 1: EXP Total**:
  - Linha temporal de experiência total do mundo
  - Filtro de período: 7, 15, 30, 45, 90, 180 dias, Todos
  - **Preenche até hoje** automaticamente
- **Gráfico 2: Personagens Ativos**:
  - Linha temporal de número de personagens ativos
  - Mesmo filtro de período
  - **Preenche até hoje** automaticamente
- **Ranking de Experiência**:
  - Tabela com top 100
  - Gráfico de barras (top 10)
  - Filtros:
    - Tipo: Acumulada ou Média Diária
    - Período: 7, 15, 30, 45, 90, 180 dias, Todos
  - Colunas: Rank, Nome, Nível, Mundo, Vocação, Guild, EXP
  - **Ordenação**: Decrescente por experiência
  - **Valores**: Arredondados para cima (inteiros)

**Layout:**

- Gráficos lado a lado (50% cada) em telas médias/grandes
- Ranking abaixo com tabela e gráfico lado a lado
- Gráfico de ranking ocupa altura completa da div (minHeight: 600px)

#### 5. Componente: Cookie Consent

- Banner de consentimento de cookies
- Armazena preferência em `localStorage`
- Persiste entre sessões

---

## 🔄 Fluxos de Dados

### Fluxo 1: Atualização Diária Automática

```
00:01 (Brasília) - Scheduler dispara
    │
    ├─→ update_all_characters()
    │   │
    │   ├─→ Para cada personagem no banco:
    │   │   │
    │   │   ├─→ scrape_character_data(name, world, use_cache=False)
    │   │   │   │
    │   │   │   ├─→ get_character_html() [com timeout 25s]
    │   │   │   │   ├─→ Requisição HTTP para Taleon
    │   │   │   │   └─→ Cache Redis (5min) se use_cache=True
    │   │   │   │
    │   │   │   ├─→ Parse HTML (BeautifulSoup)
    │   │   │   │   ├─→ Extrai: level, exp, daily_exp, deaths, guild, outfit
    │   │   │   │   └─→ Valida se personagem existe
    │   │   │   │
    │   │   │   ├─→ download_outfit() [se houver URL]
    │   │   │   │   └─→ Salva em /app/static/outfits/
    │   │   │   │
    │   │   │   └─→ Persiste em CHARACTER_HISTORY
    │   │   │       ├─→ Verifica duplicata (mesmo dia)
    │   │   │       └─→ Cria ou atualiza registro
    │   │   │
    │   │   └─→ Delay 2s entre requisições
    │   │
    │   └─→ Log: Total, Sucesso, Erros
```

### Fluxo 2: Descoberta Automática de Personagens

```
23:00 (Brasília) - Scheduler dispara
    │
    ├─→ discover_and_add_characters()
    │   │
    │   ├─→ fetch_and_extract_characters() [Paralelo]
    │   │   ├─→ aura_powergamers.php
    │   │   ├─→ san_powergamers.php
    │   │   ├─→ aura_deaths.php
    │   │   └─→ san_deaths.php
    │   │
    │   ├─→ extract_characters_from_table()
    │   │   ├─→ Parse HTML
    │   │   ├─→ Encontra links characterprofile.php
    │   │   └─→ Extrai nomes (decodifica URL encoding)
    │   │
    │   ├─→ Agrupa por fonte (detecta mundo)
    │   │
    │   └─→ Para cada nome único:
    │       ├─→ Verifica se já existe no banco
    │       └─→ Se não existe: INSERT em CHARACTERS
    │           └─→ level=0, vocation="", world={detectado}
```

### Fluxo 3: Visualização de Gráfico de Personagem

```
Usuário acessa /characters/330?days=30
    │
    ├─→ Frontend: GET /api/characters/330?days=30
    │   │
    │   ├─→ Backend: get_character(330, days=30)
    │   │   │
    │   │   ├─→ Busca CHARACTER com history (joinedload)
    │   │   │
    │   │   ├─→ Filtra history por cutoff_date (se days > 0)
    │   │   │
    │   │   ├─→ enrich_character_response()
    │   │   │   ├─→ Ordena history por timestamp (desc)
    │   │   │   ├─→ Pega latest_history (real, id > 0)
    │   │   │   ├─→ Calcula daily_experience:
    │   │   │   │   ├─→ Se há 2+ registros reais: diff entre últimos 2
    │   │   │   │   └─→ Senão: usa daily_experience do registro
    │   │   │   └─→ Retorna response com history
    │   │   │
    │   │   └─→ Preenche dias faltantes:
    │   │       ├─→ Separa registros reais (id > 0) dos preenchidos
    │   │       ├─→ Determina período (start_date até last_real_date)
    │   │       ├─→ Para cada dia:
    │   │       │   ├─→ Se existe registro real: usa ele
    │   │       │   └─→ Senão: cria com exp=0, level=last_level
    │   │       └─→ Retorna history preenchido
    │   │
    │   └─→ Frontend: Renderiza gráfico
    │       ├─→ Ordena history por timestamp (asc) para gráfico
    │       ├─→ Calcula média diária (se aplicável)
    │       └─→ Chart.js: Linha dupla (Nível + Experiência)
```

### Fluxo 4: Cálculo de Ranking

```
Usuário acessa /stats e seleciona tipo "Média Diária"
    │
    ├─→ Frontend: GET /api/ranking/experience?type=average&days=30&world=san&limit=100
    │   │
    │   ├─→ Backend: get_experience_ranking()
    │   │   │
    │   │   ├─→ Calcula cutoff_date (hoje - days)
    │   │   │
    │   │   ├─→ Query: MIN(exp), MAX(exp) no período por personagem
    │   │   │   └─→ Filtra por mundo (JOIN com CHARACTERS)
    │   │   │
    │   │   ├─→ Para cada personagem:
    │   │   │   ├─→ total_exp_gained = MAX(exp) - MIN(exp)
    │   │   │   ├─→ avg_exp = total_exp_gained / interval_days
    │   │   │   └─→ Se avg_exp > 0: adiciona ao ranking
    │   │   │
    │   │   ├─→ Busca informações adicionais:
    │   │   │   ├─→ Nome, vocação, guild (CHARACTERS)
    │   │   │   └─→ Level mais recente (CHARACTER_HISTORY)
    │   │   │
    │   │   ├─→ Ordena por avg_exp (desc)
    │   │   │
    │   │   └─→ Aplica limit (100) e Math.ceil() nos valores
    │   │
    │   └─→ Frontend: Renderiza tabela e gráfico
    │       ├─→ Tabela: top 100 ordenados
    │       └─→ Gráfico: top 10 em barras
```

---

## ⏰ Tarefas Agendadas

### 1. Atualização Diária de Personagens

**Agendamento:** `00:01` (Brasília) - Todos os dias

**Função:** `update_all_characters()`

**Processamento:**

```python
Para cada personagem em CHARACTERS:
  1. scrape_character_data(name, world, use_cache=False)
  2. Delay 2s entre requisições
  3. Timeout 30s por personagem
  4. Log de progresso: [idx/total]
  5. Estatísticas finais: Total, Sucesso, Erros
```

**Complexidade:** O(n) onde n = número de personagens

### 2. Descoberta Automática de Personagens

**Agendamento:** `23:00` (Brasília) - Todos os dias

**Função:** `discover_and_add_characters()`

**Processamento:**

```python
1. Busca personagens de 4 fontes (paralelo):
   - Powergamers Aura
   - Powergamers San
   - Deaths Aura
   - Deaths San

2. Extrai nomes únicos

3. Para cada nome:
   - Verifica se já existe
   - Se não existe: cria em CHARACTERS
   - Detecta mundo pela fonte

4. Retorna estatísticas
```

**Complexidade:** O(n) onde n = personagens encontrados

---

## 🔌 APIs e Endpoints

### Resumo de Endpoints

| Método | Endpoint | Descrição | Parâmetros |
|--------|----------|-----------|------------|
| GET | `/api/characters` | Lista personagens | - |
| GET | `/api/characters/{id}` | Detalhes do personagem | `days` (query) |
| POST | `/api/characters` | Criar personagem | Body: `{name, world}` |
| POST | `/api/characters/{id}/update` | Atualizar manualmente | - |
| POST | `/api/characters/update-all` | Atualizar todos | - |
| POST | `/api/characters/discover` | Descobrir novos | - |
| DELETE | `/api/characters/{id}` | Deletar personagem | - |
| GET | `/api/stats/worlds` | Lista mundos | - |
| GET | `/api/stats/worlds/{world}/exp-history` | Histórico EXP | `days` (query) |
| GET | `/api/stats/worlds/{world}/active-history` | Histórico ativos | `days` (query) |
| POST | `/api/stats/worlds/{world}/calculate-stats` | Calcular stats | - |
| POST | `/api/stats/worlds/{world}/fill-missing-days` | Preencher dias | `days` (query) |
| GET | `/api/ranking/experience` | Ranking de EXP | `days`, `limit`, `world`, `type` |
| GET | `/api/favorites` | Lista favoritos | - |
| POST | `/api/favorites/{id}` | Adicionar favorito | - |
| DELETE | `/api/favorites/{id}` | Remover favorito | - |
| GET | `/api/health` | Health check | - |

### Formato de Respostas

#### Character Response

```json
{
  "id": 330,
  "name": "The Crusty",
  "level": 1427,
  "vocation": "Royal Paladin",
  "world": "san",
  "guild": "Guild Name",
  "outfit": "/api/static/outfits/330_san_outfit.php.png",
  "experience": 505112145.0,
  "daily_experience": 101564362.0,
  "last_updated": "2025-12-23T20:41:14",
  "history": [
    {
      "id": 1234,
      "character_id": 330,
      "level": 1427,
      "experience": 505112145.0,
      "daily_experience": 101564362.0,
      "deaths": 0,
      "timestamp": "2025-12-23T20:41:14"
    }
  ]
}
```

#### Server Stats Response

```json
{
  "id": 1,
  "world": "san",
  "total_experience": 50000000000.0,
  "active_characters": 624,
  "timestamp": "2025-12-24T00:00:00"
}
```

---

## 🖥️ Interface do Usuário

### Estrutura de Navegação

```
┌─────────────────────────────────────────┐
│  Navbar (TaleonTracker)                 │
│  [Personagens] [Estatísticas] [Comparar] │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
    ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
    │ Lista │  │ Stats │  │Compare│
    └───────┘  └───────┘  └───────┘
        │
    ┌───▼───────┐
    │ Detalhes  │
    │ (/:id)    │
    └───────────┘
```

### Componentes Reutilizáveis

1. **Navbar**: Navegação principal, links para todas as páginas
2. **CookieConsent**: Banner de consentimento (persistente)
3. **AddCharacterForm**: (Removido - não mais usado)

### Tema e Estilo

- **Tema**: Material-UI Dark Mode
- **Cores**: 
  - Primary: `#90caf9` (azul claro)
  - Secondary: `#f48fb1` (rosa)
- **Layout**: 80% de largura, centralizado, max-width 1400px

---

## 🔗 Relacionamentos entre Funcionalidades

### Dependências

```
SCRAPER
  │
  ├─→ CHARACTER_HISTORY (cria registros)
  │   └─→ Usado por: Rankings, Gráficos, Estatísticas
  │
  ├─→ CHARACTERS (atualiza dados)
  │   └─→ Usado por: Lista, Detalhes, Comparação
  │
  └─→ OUTFIT_DOWNLOADER (baixa imagens)
      └─→ Usado por: Lista, Detalhes, Comparação

CHARACTER_DISCOVERY
  │
  └─→ CHARACTERS (cria novos)
      └─→ Será atualizado pelo SCRAPER na próxima execução

FILL_MISSING_DAYS
  │
  ├─→ SERVER_STATS (preenche)
  │   └─→ Usado por: Gráficos de mundo
  │
  └─→ CHARACTER_HISTORY (preenche em memória)
      └─→ Usado por: Gráficos de personagem

RANKING
  │
  ├─→ CHARACTER_HISTORY (lê)
  └─→ CHARACTERS (lê)
      └─→ Calcula: Acumulada ou Média Diária

SERVER_STATS
  │
  ├─→ CHARACTER_HISTORY (agrega)
  └─→ CHARACTERS (filtra por mundo)
      └─→ Calcula: EXP Total, Personagens Ativos
```

### Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    FONTES EXTERNAS                          │
│  - san.taleon.online/characterprofile.php                  │
│  - aura.taleon.online/characterprofile.php                  │
│  - san.taleon.online/powergamers.php                        │
│  - aura.taleon.online/powergamers.php                       │
│  - san.taleon.online/deaths.php                             │
│  - aura.taleon.online/deaths.php                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌────▼─────┐
│   SCRAPER    │ │ DISCOVERY  │ │  CACHE   │
│  (diário)    │ │  (diário)  │ │  (Redis) │
└───────┬──────┘ └─────┬──────┘ └──────────┘
        │              │
        └──────┬───────┘
               │
    ┌──────────▼──────────┐
    │   POSTGRESQL        │
    │  - CHARACTERS       │
    │  - CHARACTER_HISTORY│
    │  - SERVER_STATS     │
    │  - FAVORITES        │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │      BACKEND        │
    │  - Enriquecimento   │
    │  - Agregações       │
    │  - Preenchimento    │
    │  - Rankings         │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │      FRONTEND       │
    │  - Visualizações    │
    │  - Gráficos         │
    │  - Filtros          │
    └─────────────────────┘
```

---

## 📝 Notas Técnicas Importantes

### Tratamento de Dados Faltantes

1. **Registros Preenchidos (id=0)**:
   - Criados automaticamente para preencher lacunas
   - **Nunca usados** em cálculos de level, experience ou daily_experience
   - Apenas para visualização contínua em gráficos

2. **Experiência = 0**:
   - Quando não há dados: `experience = 0` (não repete do dia anterior)
   - Quando não há mudança: `daily_experience = 0`
   - Quando personagem não encontrado: cria registro com `daily_experience = 0`

3. **Level Mantido**:
   - Quando não há dados: mantém `level` do último registro real
   - Faz sentido: level não diminui, apenas experiência pode ser 0

### Performance

- **Cache Redis**: HTML cacheado por 5 minutos
- **Queries Otimizadas**: Uso de índices, JOINs eficientes
- **Processamento Assíncrono**: Scraping e descoberta não bloqueiam API
- **Timeout Protection**: Timeouts em todas as requisições HTTP

### Segurança

- **CORS**: Configurado para permitir todas as origens (desenvolvimento)
- **Validação**: Validação de mundos (apenas san/aura)
- **Sanitização**: Limpeza de dados extraídos (remove formatação)

---

## 🎯 Conclusão

O **TaleonTracker** é um sistema completo de monitoramento que:

1. **Coleta dados automaticamente** de múltiplas fontes
2. **Armazena histórico completo** de evolução
3. **Processa e agrega** dados para análises
4. **Visualiza informações** de forma interativa
5. **Descobre novos personagens** automaticamente

Todos os componentes trabalham em conjunto para fornecer uma experiência completa de monitoramento e análise de personagens do Taleon Online.

