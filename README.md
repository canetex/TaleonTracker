# TaleonTracker

Sistema de rastreamento de personagens do Taleon Online.

## Descrição

O TaleonTracker é uma aplicação web que monitora automaticamente a evolução de personagens no jogo Taleon Online. O sistema extrai dados diariamente e apresenta visualizações interativas do progresso dos personagens.

## Funcionalidades

- Extração automática diária de dados de personagens
- Monitoramento de nível, experiência e mortes
- Interface web com gráficos interativos
- Atualização manual dos dados
- Suporte a múltiplos personagens

## Tecnologias Utilizadas

- Backend: Python (FastAPI)
- Frontend: React + TypeScript
- Banco de Dados: PostgreSQL
- Container: Docker
- Gráficos: Chart.js

## Requisitos

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker e Docker Compose

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/canetex/TaleonTracker.git
cd TaleonTracker
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Inicie os containers:
```bash
docker-compose up -d
```

4. Acesse a aplicação em `https://seu-dominio:3000`
   Acesse o backend em `https://seu-dominio:8000`

## Estrutura do Projeto

```
TaleonTracker/
├── backend/           # API FastAPI
├── frontend/         # Aplicação React
├── database/         # Scripts e migrações do banco
├── docker/           # Configurações Docker
└── docs/            # Documentação
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 

## Desenvolvimento

1. Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

2. Frontend:
```bash
cd frontend
npm install
npm start
```

## Próximos Passos

1. Implementar autenticação de usuários
2. Adicionar mais métricas e gráficos
3. Implementar notificações
4. Adicionar testes automatizados
5. Melhorar a documentação
6. Implementar cache para melhor performance
7. Adicionar suporte a múltiplos servidores

Você pode começar a usar o sistema agora! Basta seguir as instruções de configuração e execução acima. Se tiver alguma dúvida ou precisar de ajuda, estou à disposição. 