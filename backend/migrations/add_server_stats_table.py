#!/usr/bin/env python3
"""
Script de migração para adicionar tabela server_stats
Este script preserva todos os dados existentes no banco de dados
Complexidade: O(1) - operação de criação de tabela
"""

import sys
import os

# Adiciona o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """
    Adiciona a tabela server_stats ao banco de dados existente
    """
    try:
        logger.info("Iniciando migração: adicionando tabela server_stats...")
        
        with engine.connect() as conn:
            # Verifica se a tabela já existe
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'server_stats'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                logger.info("Tabela server_stats já existe. Migração não necessária.")
                return
            
            # Cria a tabela server_stats
            logger.info("Criando tabela server_stats...")
            conn.execute(text("""
                CREATE TABLE server_stats (
                    id SERIAL PRIMARY KEY,
                    world VARCHAR NOT NULL,
                    total_experience FLOAT NOT NULL DEFAULT 0,
                    active_characters INTEGER NOT NULL DEFAULT 0,
                    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Cria índices para melhor performance
            logger.info("Criando índices...")
            conn.execute(text("""
                CREATE INDEX idx_server_stats_world ON server_stats(world)
            """))
            conn.execute(text("""
                CREATE INDEX idx_server_stats_timestamp ON server_stats(timestamp)
            """))
            
            conn.commit()
            logger.info("Migração concluída com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro durante a migração: {str(e)}")
        raise

if __name__ == "__main__":
    migrate()

