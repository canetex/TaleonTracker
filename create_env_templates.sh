#!/bin/bash

# Criar template do backend
cat > backend/.env.template << 'EOF'
# Configurações do Banco de Dados
DB_NAME=taleontracker
DB_USER=taleon
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# Configurações do Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here

# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
SECRET_KEY=your_secret_key_here

# Configurações de CORS
CORS_ORIGINS=["http://localhost:3000", "https://seu-dominio.com"]

# Configurações de Log
LOG_LEVEL=INFO
LOG_FILE=/var/log/taleontracker/backend.log

# Configurações de Segurança
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF

# Criar template do frontend
cat > frontend/.env.template << 'EOF'
# Configurações da API
REACT_APP_API_URL=your_api_url_here

# Configurações de Ambiente
NODE_ENV=production
PORT=3000

# Configurações de Build
GENERATE_SOURCEMAP=false
EOF

# Tornar o script executável
chmod +x create_env_templates.sh

echo "Templates de ambiente criados com sucesso!" 