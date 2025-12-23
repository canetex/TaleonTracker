#!/bin/bash

# Script para executar testes do TaleonTracker

echo "🧪 Executando testes do TaleonTracker..."

# Verificar se o pytest está instalado
if ! command -v pytest &> /dev/null; then
    echo "❌ Pytest não está instalado. Instalando..."
    pip install pytest httpx
fi

# Executar testes com cobertura
echo "📊 Executando testes com cobertura..."
pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Executar testes específicos (opcional)
echo ""
echo "🎯 Executando testes específicos..."
echo "Testes de personagens:"
pytest tests/test_characters.py -v

echo ""
echo "🔐 Testes de autenticação:"
pytest tests/test_auth.py -v

echo ""
echo "💚 Testes de health check:"
pytest tests/test_health.py -v

echo ""
echo "✅ Testes concluídos!"
echo "📁 Relatório de cobertura disponível em: htmlcov/index.html" 