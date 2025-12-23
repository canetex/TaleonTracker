import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from models.character import Character

class TestCharactersAPI:
    """Testes para os endpoints de personagens"""
    
    def test_create_character(self, client: TestClient, sample_character_data):
        """Testa a criação de um personagem"""
        response = client.post("/api/characters/", json={"name": sample_character_data["name"]})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_character_data["name"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_duplicate_character(self, client: TestClient, sample_character_data):
        """Testa a criação de um personagem duplicado"""
        # Criar primeiro personagem
        client.post("/api/characters/", json={"name": sample_character_data["name"]})
        
        # Tentar criar o mesmo personagem novamente
        response = client.post("/api/characters/", json={"name": sample_character_data["name"]})
        assert response.status_code == 400
        assert "já existe" in response.json()["detail"]
    
    def test_list_characters(self, client: TestClient, sample_character_data):
        """Testa a listagem de personagens"""
        # Criar um personagem primeiro
        client.post("/api/characters/", json={"name": sample_character_data["name"]})
        
        # Listar personagens
        response = client.get("/api/characters/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_character(self, client: TestClient, sample_character_data):
        """Testa a obtenção de um personagem específico"""
        # Criar um personagem
        create_response = client.post("/api/characters/", json={"name": sample_character_data["name"]})
        character_id = create_response.json()["id"]
        
        # Obter o personagem
        response = client.get(f"/api/characters/{character_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == character_id
        assert data["name"] == sample_character_data["name"]
    
    def test_get_nonexistent_character(self, client: TestClient):
        """Testa a obtenção de um personagem que não existe"""
        response = client.get("/api/characters/999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]
    
    def test_delete_character(self, client: TestClient, sample_character_data):
        """Testa a exclusão de um personagem"""
        # Criar um personagem
        create_response = client.post("/api/characters/", json={"name": sample_character_data["name"]})
        character_id = create_response.json()["id"]
        
        # Excluir o personagem
        response = client.delete(f"/api/characters/{character_id}")
        assert response.status_code == 200
        assert "excluído" in response.json()["message"]
        
        # Verificar se foi realmente excluído
        get_response = client.get(f"/api/characters/{character_id}")
        assert get_response.status_code == 404

class TestCharacterValidation:
    """Testes de validação de dados de personagens"""
    
    def test_create_character_without_name(self, client: TestClient):
        """Testa a criação de personagem sem nome"""
        response = client.post("/api/characters/", json={})
        assert response.status_code == 422  # Validation error
    
    def test_create_character_with_empty_name(self, client: TestClient):
        """Testa a criação de personagem com nome vazio"""
        response = client.post("/api/characters/", json={"name": ""})
        assert response.status_code == 422  # Validation error
    
    def test_create_character_with_invalid_data(self, client: TestClient):
        """Testa a criação de personagem com dados inválidos"""
        response = client.post("/api/characters/", json={"name": 123})  # Nome como número
        assert response.status_code == 422  # Validation error 