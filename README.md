# TaleonTracker

Sistema de rastreamento e gerenciamento de evolução dos Chars.

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

## Requisitos do Sistema

- Python 3.8 ou superior
- Node.js 14 ou superior
- NPM 6 ou superior
- PostgreSQL 12 ou superior
- Redis 6 ou superior
- 1GB de espaço em disco livre
- Acesso root para instalação

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/canetex/TaleonTracker.git
cd TaleonTracker
```

2. Execute o script de instalação como root:
```bash
sudo ./setup_complete.sh
```

O script irá:
- Verificar e instalar dependências necessárias
- Configurar o firewall
- Configurar o PostgreSQL com senha aleatória
- Criar backup da instalação anterior (se existir)
- Configurar permissões e diretórios
- Iniciar os serviços necessários

## Arquivos de Configuração

- `config.sh`: Contém todas as variáveis de configuração
- `utils.sh`: Funções utilitárias reutilizáveis
- `setup_complete.sh`: Script principal de instalação

## Logs

Os logs de instalação são armazenados em:
- `/var/log/taleontracker/install.log`

## Segurança

- Senhas são geradas aleatoriamente durante a instalação
- Arquivos de senha são armazenados com permissões restritas
- Firewall é configurado automaticamente
- Verificações de versão e dependências são realizadas

## Backup

Backups são criados automaticamente antes de:
- Remover instalação anterior
- Atualizar o sistema

Os backups são armazenados em:
- `/var/backups/taleontracker/`

## Troubleshooting

Se encontrar problemas durante a instalação:

1. Verifique os logs:
```bash
cat /var/log/taleontracker/install.log
```

2. Verifique o status dos serviços:
```bash
sudo systemctl status taleontracker
sudo systemctl status postgresql
sudo systemctl status nginx
```

3. Verifique as permissões:
```bash
ls -la /opt/taleontracker
ls -la /etc/taleontracker
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Estrutura do Projeto

```
TaleonTracker/
├── backend/           # API FastAPI
├── frontend/         # Aplicação React
├── database/         # Scripts e migrações do banco
├── docker/           # Configurações Docker
└── docs/            # Documentação
```

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