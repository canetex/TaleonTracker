# 🔗 Grafo de Relacionamentos entre Funções - TaleonTracker

Este documento apresenta os grafos de relacionamento entre todas as funções da aplicação, mostrando como elas se conectam e interagem.

## 📊 Formato dos Grafos

Os grafos estão em formato **Mermaid**, que pode ser visualizado em:
- GitHub (renderiza automaticamente)
- Editores como VS Code (com extensão Mermaid)
- Ferramentas online: https://mermaid.live

---

## 🎯 Grafo Principal - Visão Geral do Sistema

```mermaid
graph TB
    subgraph "Frontend (React)"
        A[App.tsx] --> B[Navbar]
        A --> C[CharacterList]
        A --> D[CharacterDetail]
        A --> E[CharacterCompare]
        A --> F[WorldStats]
        A --> G[CookieConsent]
        
        C --> H[api.getCharacters]
        D --> I[api.getCharacterHistory]
        E --> J[api.getCharacters - múltiplos]
        F --> K[api.getWorldStats]
        F --> L[api.getRanking]
        
        H --> M[Backend API]
        I --> M
        J --> M
        K --> M
        L --> M
    end
    
    subgraph "Backend (FastAPI)"
        M --> N[characters.router]
        M --> O[server_stats.router]
        M --> P[character_ranking.router]
        M --> Q[favorites.router]
        
        N --> R[enrich_character_response]
        N --> S[scrape_character_data]
        N --> T[update_all_characters]
        N --> U[discover_and_add_characters]
        
        O --> V[fill_missing_days_for_world]
        O --> W[calculate_world_stats]
        
        P --> X[get_experience_ranking]
    end
    
    subgraph "Services"
        S --> Y[get_character_html]
        S --> Z[download_outfit]
        T --> S
        U --> AA[fetch_and_extract_characters]
        U --> AB[extract_characters_from_table]
        V --> AC[fill_missing_days_for_world]
    end
    
    subgraph "Scheduler"
        AD[BackgroundScheduler] --> T
        AD --> U
    end
    
    subgraph "Database"
        R --> AE[(PostgreSQL)]
        S --> AE
        T --> AE
        U --> AE
        V --> AE
        W --> AE
        X --> AE
    end
    
    subgraph "Cache"
        Y --> AF[(Redis)]
    end
    
    subgraph "External"
        Y --> AG[Taleon Website]
        AA --> AG
        Z --> AG
    end
```

---

## 🔄 Grafo Detalhado - Backend Services

```mermaid
graph LR
    subgraph "Scraper Service"
        A[scrape_character_data] --> B[get_character_html]
        A --> C[download_outfit]
        A --> D[(CharacterHistory INSERT)]
        A --> E[(Character UPDATE)]
        
        B --> F[(Redis Cache)]
        B --> G[Taleon HTTP Request]
        
        C --> H[Salva em /app/static/outfits/]
        
        I[update_all_characters] --> A
        I --> J[Loop: todos personagens]
        I --> K[Delay 2s entre requisições]
    end
    
    subgraph "Character Discovery"
        L[discover_and_add_characters] --> M[fetch_and_extract_characters]
        M --> N[extract_characters_from_table]
        N --> O[Parse HTML]
        N --> P[Extrai links characterprofile.php]
        N --> Q[Decodifica nomes]
        
        L --> R[(Character INSERT)]
        L --> S[Detecta mundo pela fonte]
    end
    
    subgraph "Fill Missing Days"
        T[fill_missing_days_for_world] --> U[Busca registros existentes]
        T --> V[Identifica lacunas]
        T --> W[Cria registros com exp=0]
        T --> X[(ServerStats INSERT)]
    end
    
    subgraph "Outfit Downloader"
        Y[download_outfit] --> Z[Parse URL]
        Y --> AA[HTTP GET imagem]
        Y --> AB[Salva arquivo local]
        Y --> AC[Retorna caminho /api/static/outfits/]
    end
```

---

## 🎨 Grafo Detalhado - Frontend Components

```mermaid
graph TB
    subgraph "App.tsx - Router Principal"
        A[App] --> B[BrowserRouter]
        B --> C[Routes]
        C --> D[/characters]
        C --> E[/characters/:id]
        C --> F[/characters/compare]
        C --> G[/stats]
    end
    
    subgraph "CharacterList.tsx"
        D --> H[CharacterList]
        H --> I[useState: characters, filters]
        H --> J[useEffect: fetchCharacters]
        J --> K[api.getCharacters]
        K --> L[setCharacters]
        H --> M[useMemo: filteredCharacters]
        M --> N[Filtros: nome, mundo, guild, favoritos, EXP dias]
        H --> O[handleToggleFavorite]
        O --> P[api.addFavorite / removeFavorite]
        H --> Q[Grid de Cards]
    end
    
    subgraph "CharacterDetail.tsx"
        E --> R[CharacterDetail]
        R --> S[useParams: id]
        R --> T[useState: character, daysFilter]
        R --> U[useEffect: fetchCharacter]
        U --> V[api.getCharacterHistory]
        V --> W[setCharacter]
        R --> X[useMemo: history filtrado]
        X --> Y[Calcula averageDailyExp]
        R --> Z[Line Chart - Nível + EXP]
        R --> AA[handleUpdate]
        AA --> AB[api.updateCharacter]
    end
    
    subgraph "CharacterCompare.tsx"
        F --> AC[CharacterCompare]
        AC --> AD[useState: selectedCharacters]
        AC --> AE[api.getCharacters - múltiplos]
        AC --> AF[Compara stats lado a lado]
        AC --> AG[Line Chart comparativo]
    end
    
    subgraph "WorldStats.tsx"
        G --> AH[WorldStats]
        AH --> AI[useState: worlds, selectedWorld, stats]
        AH --> AJ[useEffect: fetchWorlds]
        AJ --> AK[api.getWorlds]
        AH --> AL[useEffect: fetchStats]
        AL --> AM[api.getExpHistory]
        AL --> AN[api.getActiveHistory]
        AH --> AO[useEffect: fetchRanking]
        AO --> AP[api.getRanking]
        AH --> AQ[Line Chart: EXP Total]
        AH --> AR[Line Chart: Personagens Ativos]
        AH --> AS[Table + Bar Chart: Ranking]
    end
    
    subgraph "API Service"
        K --> AT[api.ts]
        V --> AT
        AE --> AT
        AK --> AT
        AM --> AT
        AN --> AT
        AP --> AT
        P --> AT
        AB --> AT
        
        AT --> AU[axios.create baseURL: /api]
        AU --> AV[HTTP Requests]
    end
```

---

## 🔀 Grafo de Fluxo de Dados - Scraping

```mermaid
sequenceDiagram
    participant Scheduler
    participant update_all_characters
    participant scrape_character_data
    participant get_character_html
    participant Redis
    participant Taleon
    participant download_outfit
    participant Database
    
    Scheduler->>update_all_characters: 00:01 (diário)
    update_all_characters->>Database: SELECT * FROM characters
    loop Para cada personagem
        update_all_characters->>scrape_character_data: name, world, use_cache=False
        scrape_character_data->>get_character_html: name, world, use_cache=False
        get_character_html->>Redis: Verifica cache
        alt Cache hit
            Redis-->>get_character_html: HTML cacheado
        else Cache miss
            get_character_html->>Taleon: HTTP GET characterprofile.php
            Taleon-->>get_character_html: HTML response
            get_character_html->>Redis: Salva cache (5min)
        end
        get_character_html-->>scrape_character_data: HTML, world_detected
        scrape_character_data->>scrape_character_data: Parse HTML (BeautifulSoup)
        scrape_character_data->>scrape_character_data: Extrai: level, exp, daily_exp, deaths, guild
        alt Outfit encontrado
            scrape_character_data->>download_outfit: outfit_url, character_id, world
            download_outfit->>Taleon: HTTP GET imagem
            Taleon-->>download_outfit: Imagem binária
            download_outfit->>download_outfit: Salva em /app/static/outfits/
            download_outfit-->>scrape_character_data: /api/static/outfits/{filename}
        end
        scrape_character_data->>Database: UPDATE characters
        scrape_character_data->>Database: INSERT character_history
        scrape_character_data-->>update_all_characters: True/False
        update_all_characters->>update_all_characters: Delay 2s
    end
    update_all_characters->>update_all_characters: Log estatísticas finais
```

---

## 🔀 Grafo de Fluxo de Dados - Descoberta de Personagens

```mermaid
sequenceDiagram
    participant Scheduler
    participant discover_and_add_characters
    participant fetch_and_extract_characters
    participant extract_characters_from_table
    participant Taleon
    participant Database
    
    Scheduler->>discover_and_add_characters: 23:00 (diário)
    
    par Requisições Paralelas
        discover_and_add_characters->>fetch_and_extract_characters: aura_powergamers.php
        fetch_and_extract_characters->>Taleon: HTTP GET
        Taleon-->>fetch_and_extract_characters: HTML
        fetch_and_extract_characters->>extract_characters_from_table: HTML
        extract_characters_from_table-->>discover_and_add_characters: Set de nomes
    and
        discover_and_add_characters->>fetch_and_extract_characters: san_powergamers.php
        fetch_and_extract_characters->>Taleon: HTTP GET
        Taleon-->>fetch_and_extract_characters: HTML
        fetch_and_extract_characters->>extract_characters_from_table: HTML
        extract_characters_from_table-->>discover_and_add_characters: Set de nomes
    and
        discover_and_add_characters->>fetch_and_extract_characters: aura_deaths.php
        fetch_and_extract_characters->>Taleon: HTTP GET
        Taleon-->>fetch_and_extract_characters: HTML
        fetch_and_extract_characters->>extract_characters_from_table: HTML
        extract_characters_from_table-->>discover_and_add_characters: Set de nomes
    and
        discover_and_add_characters->>fetch_and_extract_characters: san_deaths.php
        fetch_and_extract_characters->>Taleon: HTTP GET
        Taleon-->>fetch_and_extract_characters: HTML
        fetch_and_extract_characters->>extract_characters_from_table: HTML
        extract_characters_from_table-->>discover_and_add_characters: Set de nomes
    end
    
    discover_and_add_characters->>discover_and_add_characters: Unifica todos os sets
    discover_and_add_characters->>discover_and_add_characters: Detecta mundo por fonte
    
    loop Para cada nome único
        discover_and_add_characters->>Database: SELECT WHERE name = ?
        alt Não existe
            discover_and_add_characters->>Database: INSERT INTO characters
            Database-->>discover_and_add_characters: Sucesso
        else Já existe
            Database-->>discover_and_add_characters: Ignora
        end
    end
    
    discover_and_add_characters-->>Scheduler: Estatísticas
```

---

## 🔀 Grafo de Fluxo - Enriquecimento de Resposta

```mermaid
graph TD
    A[get_character endpoint] --> B[Busca Character com history]
    B --> C{Filtra por days?}
    C -->|days > 0| D[Filtra history por cutoff_date]
    C -->|days = 0| E[Usa todo history]
    D --> F[enrich_character_response]
    E --> F
    
    F --> G[Ordena history por timestamp desc]
    G --> H[Separa registros reais id > 0]
    H --> I[latest_history = real_history[0]]
    H --> J[previous_history = real_history[1]]
    
    I --> K{Calcula daily_experience}
    K -->|2+ registros reais| L[diff = latest.exp - previous.exp]
    K -->|1 registro real| M[usa latest.daily_experience]
    K -->|0 registros| N[daily_experience = 0]
    
    L --> O[Monta response]
    M --> O
    N --> O
    
    O --> P{Preenche dias faltantes?}
    P -->|Sim| Q[Separa real vs preenchido]
    Q --> R[Determina período]
    R --> S[Loop: cada dia no período]
    S --> T{Existe registro real?}
    T -->|Sim| U[Usa registro real]
    T -->|Não| V[Cria com exp=0, level=last]
    U --> W[filled_history]
    V --> W
    W --> X[Retorna response]
    P -->|Não| X
```

---

## 🔀 Grafo de Fluxo - Cálculo de Ranking

```mermaid
graph TD
    A[get_experience_ranking] --> B{Tipo?}
    
    B -->|accumulated| C[Busca MAX exp no período]
    B -->|average| D[Busca MIN e MAX exp no período]
    
    C --> E[Busca MAX exp ANTES do período]
    E --> F[accumulated = MAX_periodo - MAX_antes]
    F --> G{Filtra accumulated > 0}
    
    D --> H[total_gained = MAX - MIN]
    H --> I[avg = total_gained / interval_days]
    I --> J{Filtra avg > 0}
    
    G --> K[Busca info CHARACTERS]
    J --> K
    
    K --> L[Busca level mais recente]
    L --> M[Ordena por experiência desc]
    M --> N[Aplica limit]
    N --> O[Math.ceil valores]
    O --> P[Retorna ranking]
```

---

## 🔀 Grafo de Fluxo - Preenchimento de Dias Faltantes

```mermaid
graph TD
    A[get_character com days] --> B[enrich_character_response]
    B --> C[history retornado]
    C --> D[Separa real_history id > 0]
    D --> E[Cria history_dict por data]
    
    E --> F{Determina período}
    F -->|days > 0| G[start_date = hoje - days]
    F -->|days = 0| H[start_date = primeira data real]
    
    G --> I[end_date = última data real]
    H --> I
    
    I --> J[Loop: current_date até end_date]
    J --> K{current_date em history_dict?}
    
    K -->|Sim| L[Usa registro real]
    K -->|Não| M[Cria registro preenchido]
    
    L --> N[Atualiza last_level, last_experience]
    M --> O[level = last_level]
    M --> P[experience = 0]
    M --> Q[daily_experience = 0]
    
    N --> R[filled_history.append]
    O --> R
    P --> R
    Q --> R
    
    R --> S{current_date <= end_date?}
    S -->|Sim| J
    S -->|Não| T[Retorna filled_history]
```

---

## 🔀 Grafo de Dependências - Backend Routers

```mermaid
graph LR
    subgraph "characters.router"
        A[list_characters] --> B[enrich_character_response]
        C[get_character] --> B
        C --> D[Preenche dias faltantes]
        E[create_character] --> F[scrape_character_data]
        G[update_character] --> F
        H[update_all_characters_endpoint] --> I[update_all_characters]
        J[discover_characters_endpoint] --> K[discover_and_add_characters]
    end
    
    subgraph "server_stats.router"
        L[get_world_exp_history] --> M[Calcula dinamicamente se não há stats]
        L --> N[fill_missing_days - lógica inline]
        O[get_world_active_history] --> M
        O --> N
        P[calculate_world_stats] --> Q[Agrega por mundo]
        R[fill_missing_days endpoint] --> S[fill_missing_days_for_world]
    end
    
    subgraph "character_ranking.router"
        T[get_experience_ranking] --> U{type?}
        U -->|accumulated| V[Calcula diff com exp antes]
        U -->|average| W[Calcula média: diff / days]
        V --> X[Filtra > 0]
        W --> X
        X --> Y[Ordena desc]
    end
    
    subgraph "favorites.router"
        Z[get_favorites] --> AA[(SELECT favorites)]
        AB[add_favorite] --> AC[(INSERT favorite)]
        AD[remove_favorite] --> AE[(DELETE favorite)]
    end
    
    B --> AF[(CharacterHistory)]
    F --> AG[get_character_html]
    F --> AH[download_outfit]
    I --> F
    K --> AI[fetch_and_extract_characters]
    S --> AJ[(ServerStats)]
```

---

## 🔀 Grafo de Dependências - Frontend Services

```mermaid
graph TD
    subgraph "api.ts - API Service"
        A[getCharacters] --> B[axios.get /characters]
        C[getCharacterHistory] --> D[axios.get /characters/:id?days=]
        E[addCharacter] --> F[axios.post /characters]
        G[updateCharacter] --> H[axios.post /characters/:id/update]
        I[deleteCharacter] --> J[axios.delete /characters/:id]
        K[addFavorite] --> L[axios.post /favorites/:id]
        M[removeFavorite] --> N[axios.delete /favorites/:id]
        O[getFavorites] --> P[axios.get /favorites]
    end
    
    subgraph "format.ts - Utils"
        Q[formatNumber] --> R[Intl.NumberFormat pt-BR]
        S[formatDate] --> T[Date.toLocaleString pt-BR]
        U[getOutfitUrl] --> V[Normaliza caminhos de outfit]
    end
    
    subgraph "Pages"
        W[CharacterList] --> A
        W --> K
        W --> M
        W --> O
        W --> Q
        W --> S
        W --> U
        
        X[CharacterDetail] --> C
        X --> G
        X --> Q
        X --> S
        X --> U
        
        Y[CharacterCompare] --> A
        Y --> Q
        Y --> S
        Y --> U
        
        Z[WorldStats] --> AA[api.getWorlds]
        Z --> AB[api.getExpHistory]
        Z --> AC[api.getActiveHistory]
        Z --> AD[api.getRanking]
    end
```

---

## 🔀 Grafo de Ciclo de Vida - Componentes React

```mermaid
graph TD
    subgraph "CharacterList"
        A[Component Mount] --> B[useEffect: fetchCharacters]
        B --> C[api.getCharacters]
        C --> D[setCharacters]
        D --> E[useEffect: fetchFavorites]
        E --> F[api.getFavorites]
        F --> G[setFavorites]
        
        H[User digita busca] --> I[setSearchTerm]
        I --> J[useMemo: filteredCharacters]
        
        K[User seleciona filtro] --> L[setWorldFilter / setGuildFilter]
        L --> J
        
        M[User marca favorito] --> N[handleToggleFavorite]
        N --> O[api.addFavorite / removeFavorite]
        O --> P[setFavorites]
        P --> J
        
        J --> Q[Render Grid de Cards]
    end
    
    subgraph "CharacterDetail"
        R[Component Mount] --> S[useEffect: fetchCharacter]
        S --> T[api.getCharacterHistory]
        T --> U[setCharacter]
        
        V[User muda daysFilter] --> W[setDaysFilter]
        W --> S
        
        X[User clica Atualizar] --> Y[handleUpdate]
        Y --> Z[api.updateCharacter]
        Z --> S
        
        U --> AA[useMemo: history filtrado]
        AA --> AB[Calcula averageDailyExp]
        AB --> AC[Render Gráfico]
    end
    
    subgraph "WorldStats"
        AD[Component Mount] --> AE[useEffect: fetchWorlds]
        AE --> AF[api.getWorlds]
        AF --> AG[setWorlds]
        AG --> AH[setSelectedWorld primeiro]
        
        AH --> AI[useEffect: fetchStats]
        AI --> AJ[api.getExpHistory]
        AI --> AK[api.getActiveHistory]
        AJ --> AL[setExpHistory]
        AK --> AM[setActiveHistory]
        
        AN[User muda selectedWorld] --> AO[setSelectedWorld]
        AO --> AI
        
        AP[User muda daysFilter] --> AQ[setDaysFilter]
        AQ --> AI
        
        AR[useEffect: fetchRanking] --> AS[api.getRanking]
        AS --> AT[setRanking]
        
        AU[User muda rankingType] --> AV[setRankingType]
        AV --> AR
        
        AW[User muda rankingDays] --> AX[setRankingDays]
        AX --> AR
    end
```

---

## 🔀 Grafo de Relacionamento - Scheduler e Background Tasks

```mermaid
graph TB
    subgraph "Startup (main.py)"
        A[app.on_event startup] --> B[Inicializa Redis Cache]
        A --> C[Inicializa BackgroundScheduler]
        C --> D[schedule_daily_scrape]
        C --> E[schedule_character_discovery]
        C --> F[scheduler.start]
    end
    
    subgraph "Daily Scrape (00:01)"
        D --> G[Cron: hour=0, minute=1]
        G --> H[update_all_characters]
        H --> I[Loop personagens]
        I --> J[scrape_character_data]
        J --> K[(Database)]
    end
    
    subgraph "Character Discovery (23:00)"
        E --> L[Cron: hour=23, minute=0]
        L --> M[run_discovery wrapper]
        M --> N[discover_and_add_characters]
        N --> O[fetch_and_extract_characters - 4x paralelo]
        O --> P[(Database)]
    end
    
    subgraph "Manual Triggers"
        Q[POST /characters/update-all] --> H
        R[POST /characters/discover] --> N
        S[POST /stats/worlds/{world}/fill-missing-days] --> T[fill_missing_days_for_world]
        T --> U[(ServerStats)]
    end
```

---

## 🔀 Grafo de Dependências - Modelos e Schemas

```mermaid
graph TD
    subgraph "Models (SQLAlchemy)"
        A[Character] --> B[CharacterHistory]
        A --> C[CharacterFavorite]
        D[ServerStats] -.->|Relaciona por world| A
    end
    
    subgraph "Schemas (Pydantic)"
        E[CharacterResponse] --> F[CharacterHistory schema]
        G[ServerStatsResponse] --> H[ServerStats model]
        I[RankingEntry] --> J[Character fields]
    end
    
    subgraph "Routers"
        K[characters.router] --> A
        K --> E
        L[server_stats.router] --> D
        L --> G
        M[character_ranking.router] --> A
        M --> I
        N[favorites.router] --> A
        N --> C
    end
    
    subgraph "Services"
        O[scraper] --> A
        O --> B
        P[character_discovery] --> A
        Q[fill_missing_days] --> D
    end
```

---

## 📈 Legenda dos Grafos

### Tipos de Relacionamento

- **→** : Chamada de função / dependência direta
- **-->>** : Retorno de valor / resposta
- **-.->** : Relacionamento lógico (não direto)
- **{ }** : Condição / decisão
- **[ ]** : Função / componente
- **( )** : Banco de dados / armazenamento

### Cores e Agrupamentos

- **Azul**: Frontend (React)
- **Verde**: Backend (FastAPI)
- **Amarelo**: Services
- **Roxo**: Database
- **Laranja**: External (Taleon)

---

## 🔍 Análise de Dependências

### Funções Core (Mais Importantes)

1. **`scrape_character_data`**: 
   - Chamada por: `update_all_characters`, `create_character`, `update_character`
   - Chama: `get_character_html`, `download_outfit`
   - Impacto: Alto (fonte principal de dados)

2. **`enrich_character_response`**:
   - Chamada por: Todos os endpoints de personagens
   - Chama: Nenhuma (apenas processa dados)
   - Impacto: Alto (formata todas as respostas)

3. **`discover_and_add_characters`**:
   - Chamada por: Scheduler, endpoint manual
   - Chama: `fetch_and_extract_characters`
   - Impacto: Médio (expande base de dados)

4. **`get_experience_ranking`**:
   - Chamada por: Frontend WorldStats
   - Chama: Queries complexas no banco
   - Impacto: Médio (análise de dados)

### Funções de Suporte

- **`get_character_html`**: Cache, requisições HTTP
- **`download_outfit`**: Download e salvamento de imagens
- **`fill_missing_days_for_world`**: Preenchimento de lacunas
- **`extract_characters_from_table`**: Parse de HTML para nomes

---

## 📝 Notas sobre os Grafos

1. **Fluxos Assíncronos**: Muitas funções são `async` e usam `await`
2. **Cache**: `get_character_html` usa Redis para evitar requisições duplicadas
3. **Error Handling**: Todas as funções têm tratamento de erro e logging
4. **Timeouts**: Requisições HTTP têm timeouts configurados
5. **Validação**: Dados são validados antes de persistir no banco

---

## 🎯 Conclusão

Os grafos mostram que a aplicação tem uma arquitetura bem estruturada com:

- **Separação clara** entre frontend e backend
- **Services reutilizáveis** (scraper, discovery, fill_missing_days)
- **Routers organizados** por funcionalidade
- **Dependências bem definidas** (não há dependências circulares)
- **Processamento assíncrono** para operações I/O
- **Cache estratégico** para otimização

Todas as funções trabalham em conjunto para fornecer uma experiência completa de monitoramento e análise de personagens.

