import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.character import Character
from models.character_history import CharacterHistory
from datetime import datetime
import urllib.parse
import re

def scrape_character_data(character_name: str, db: Session) -> bool:
    try:
        # URL do site do Taleon com encoding correto do nome
        encoded_name = urllib.parse.quote(character_name)
        url = f"https://san.taleon.online/characterprofile.php?name={encoded_name}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"Fazendo requisição para: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Verificar se o personagem existe
        if "Character profile of" not in response.text:
            print(f"Personagem {character_name} não encontrado")
            return False
            
        # Encontrar a tabela de informações do personagem
        tables = soup.find_all('table')
        character_info = None
        exp_info = None
        deaths_info = None
        
        for table in tables:
            if table.find('th') and 'Character profile of' in table.find('th').text:
                character_info = table
            elif table.find('th') and 'Experience History' in table.find('th').text:
                exp_info = table
            elif table.find('th') and 'Death list' in table.find('th').text:
                deaths_info = table
        
        if not character_info:
            print("Tabela de informações do personagem não encontrada")
            return False
            
        # Extrair informações básicas
        character_data = {}
        for row in character_info.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip().lower()
                value = cols[1].text.strip()
                character_data[key] = value
        
        # Extrair nível
        level_text = character_data.get('level', '0')
        level = int(re.sub(r'[^\d]', '', level_text))
        
        # Extrair vocação
        vocation = character_data.get('vocation', '')
        
        # Extrair experiência
        experience = 0
        if exp_info:
            exp_rows = exp_info.find_all('tr')
            for row in exp_rows:
                cols = row.find_all('td')
                if len(cols) >= 2 and 'today' in cols[0].text.lower():
                    exp_text = cols[1].text.strip()
                    experience = int(re.sub(r'[^\d]', '', exp_text))
                    break
        
        # Contar mortes
        deaths = 0
        if deaths_info:
            death_rows = deaths_info.find_all('tr')
            deaths = len(death_rows) - 1  # -1 para excluir o cabeçalho
        
        # Atualizar ou criar o personagem
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            character = Character(
                name=character_name,
                level=level,
                vocation=vocation,
                world='Taleon'
            )
            db.add(character)
            db.commit()
            db.refresh(character)
            print(f"Personagem criado: {character_name} (Nível {level})")
        else:
            character.level = level
            character.vocation = vocation
            character.world = 'Taleon'
            db.commit()
            print(f"Personagem atualizado: {character_name} (Nível {level})")
        
        # Criar histórico
        history = CharacterHistory(
            character_id=character.id,
            level=level,
            experience=experience,
            deaths=deaths,
            timestamp=datetime.utcnow()
        )
        
        db.add(history)
        db.commit()
        print(f"Histórico criado para: {character_name}")
        return True
        
    except Exception as e:
        print(f"Erro ao fazer scraping: {str(e)}")
        return False

def update_all_characters():
    """
    Atualiza todos os personagens cadastrados.
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        characters = db.query(Character).all()
        for character in characters:
            scrape_character_data(character.name, db)
    finally:
        db.close()
