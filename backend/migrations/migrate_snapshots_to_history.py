"""
Script para migrar dados de character_snapshots para character_history
Este script preserva todos os dados existentes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text
from datetime import datetime

def migrate_snapshots_to_history():
    """
    Migra dados de character_snapshots para character_history
    Complexidade: O(n) onde n é o número de snapshots
    """
    with engine.connect() as conn:
        # Verifica quantos snapshots existem
        result = conn.execute(text("SELECT COUNT(*) FROM character_snapshots WHERE experience > 0"))
        snapshot_count = result.scalar()
        print(f"Encontrados {snapshot_count} snapshots com experiência > 0")
        
        if snapshot_count == 0:
            print("Nenhum snapshot para migrar")
            return
        
        # Busca snapshots agrupados por character_id
        result = conn.execute(text("""
            SELECT DISTINCT character_id 
            FROM character_snapshots 
            WHERE experience > 0
        """))
        character_ids = [row[0] for row in result]
        
        migrated = 0
        for char_id in character_ids:
            # Busca snapshots do personagem ordenados por data
            result = conn.execute(text("""
                SELECT level, experience, deaths, scraped_at
                FROM character_snapshots
                WHERE character_id = :char_id AND experience > 0
                ORDER BY scraped_at ASC
            """), {"char_id": char_id})
            
            snapshots = result.fetchall()
            previous_exp = None
            
            for snapshot in snapshots:
                level, experience, deaths, scraped_at = snapshot
                
                # Calcula experiência diária
                daily_experience = 0
                if previous_exp is not None:
                    daily_experience = float(experience) - float(previous_exp)
                    if daily_experience < 0:
                        daily_experience = 0
                
                # Verifica se já existe histórico para esta data
                check_result = conn.execute(text("""
                    SELECT COUNT(*) FROM character_history
                    WHERE character_id = :char_id 
                    AND timestamp = :timestamp
                """), {"char_id": char_id, "timestamp": scraped_at})
                
                if check_result.scalar() == 0:
                    # Insere novo registro de histórico
                    conn.execute(text("""
                        INSERT INTO character_history 
                        (character_id, level, experience, daily_experience, deaths, timestamp)
                        VALUES (:char_id, :level, :experience, :daily_experience, :deaths, :timestamp)
                    """), {
                        "char_id": char_id,
                        "level": level,
                        "experience": float(experience),
                        "daily_experience": daily_experience,
                        "deaths": deaths or 0,
                        "timestamp": scraped_at
                    })
                    migrated += 1
                
                previous_exp = float(experience)
        
        conn.commit()
        print(f"Migração concluída: {migrated} registros de histórico criados")

if __name__ == "__main__":
    migrate_snapshots_to_history()
    print("Migração de snapshots para histórico concluída com sucesso!")

