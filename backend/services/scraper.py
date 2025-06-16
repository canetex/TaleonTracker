import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models.character import Character
from models.character_history import CharacterHistory
from datetime import datetime

def scrape_character_data(character_name: str, db: Session) -> bool:
    try:
        # URL do site do Taleon
        url = f"https://san.taleon.online/characterprofile.php?name={character_name}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar a tabela de informações do personagem
        character_table = soup.find('table', {'class': 'Table3'})
        if not character_table:
            print(f"Não foi possível encontrar informações para o personagem {character_name}")
            return False
            
        # Extrair informações
        rows = character_table.find_all('tr')
        character_data = {}
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip().lower()
                value = cols[1].text.strip()
                character_data[key] = value
        
        # Converter dados
        level = int(character_data.get('level', '0').replace(',', ''))
        vocation = character_data.get('vocation', '')
        world = 'Taleon'  # Mundo fixo para o Taleon
        
        # Encontrar a tabela de experiência
        exp_table = soup.find('table', {'class': 'Table4'})
        experience = 0
        if exp_table:
            exp_rows = exp_table.find_all('tr')
            for row in exp_rows:
                cols = row.find_all('td')
                if len(cols) >= 2 and 'today' in cols[0].text.lower():
                    exp_text = cols[1].text.strip().replace(',', '')
                    try:
                        experience = int(exp_text)
                    except ValueError:
                        experience = 0
                    break
        
        # Encontrar a tabela de mortes
        deaths_table = soup.find('table', {'class': 'Table5'})
        deaths = 0
        if deaths_table:
            deaths = len(deaths_table.find_all('tr')) - 1  # -1 para excluir o cabeçalho
        
        # Atualizar ou criar o personagem no banco
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            character = Character(
                name=character_name,
                level=level,
                vocation=vocation,
                world=world
            )
            db.add(character)
            db.commit()
            db.refresh(character)
        else:
            character.level = level
            character.vocation = vocation
            character.world = world
            db.commit()
        
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
