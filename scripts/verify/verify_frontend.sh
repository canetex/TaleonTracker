#!/bin/bash

echo "Verificando configuração do frontend..."

# Verificar se o Node.js está instalado
if command -v node &> /dev/null; then
    echo "✅ Node.js está instalado: $(node --version)"
else
    echo "❌ Node.js não está instalado"
fi

# Verificar se o npm está instalado
if command -v npm &> /dev/null; then
    echo "✅ npm está instalado: $(npm --version)"
else
    echo "❌ npm não está instalado"
fi

# Verificar se o PM2 está instalado
if command -v pm2 &> /dev/null; then
    echo "✅ PM2 está instalado: $(pm2 --version)"
else
    echo "❌ PM2 não está instalado"
fi

# Verificar se o diretório do frontend existe
if [ -d "/opt/taleontracker/frontend" ]; then
    echo "✅ Diretório do frontend existe"
else
    echo "❌ Diretório do frontend não existe"
fi

# Verificar se o PM2 está gerenciando o frontend
if pm2 list | grep -q "taleontracker-frontend"; then
    echo "✅ Frontend está sendo gerenciado pelo PM2"
    echo "Status do frontend:"
    pm2 show taleontracker-frontend
else
    echo "❌ Frontend não está sendo gerenciado pelo PM2"
fi

# Verificar se o frontend está respondendo
echo "Testando conexão com o frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend está respondendo"
else
    echo "❌ Frontend não está respondendo"
fi

# Mostrar últimos logs
echo "Últimos logs do frontend:"
pm2 logs taleontracker-frontend --lines 20 