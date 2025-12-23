import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

class TestAuthAPI:
    """Testes para os endpoints de autenticação"""
    
    def test_login_success(self, client: TestClient):
        """Testa login bem-sucedido"""
        response = client.post("/api/auth/token", 
                              data={"username": "admin", "password": "admin123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient):
        """Testa login com credenciais inválidas"""
        response = client.post("/api/auth/token", 
                              data={"username": "admin", "password": "wrongpassword"})
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Testa login com usuário inexistente"""
        response = client.post("/api/auth/token", 
                              data={"username": "nonexistent", "password": "admin123"})
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_get_current_user_with_valid_token(self, client: TestClient):
        """Testa obtenção do usuário atual com token válido"""
        # Primeiro fazer login para obter o token
        login_response = client.post("/api/auth/token", 
                                   data={"username": "admin", "password": "admin123"})
        token = login_response.json()["access_token"]
        
        # Usar o token para obter dados do usuário
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["full_name"] == "Administrador"
    
    def test_get_current_user_without_token(self, client: TestClient):
        """Testa obtenção do usuário atual sem token"""
        response = client.get("/api/auth/users/me")
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]
    
    def test_get_current_user_with_invalid_token(self, client: TestClient):
        """Testa obtenção do usuário atual com token inválido"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/users/me", headers=headers)
        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

class TestAuthValidation:
    """Testes de validação de dados de autenticação"""
    
    def test_login_without_username(self, client: TestClient):
        """Testa login sem nome de usuário"""
        response = client.post("/api/auth/token", 
                              data={"password": "admin123"})
        assert response.status_code == 422  # Validation error
    
    def test_login_without_password(self, client: TestClient):
        """Testa login sem senha"""
        response = client.post("/api/auth/token", 
                              data={"username": "admin"})
        assert response.status_code == 422  # Validation error
    
    def test_login_with_empty_data(self, client: TestClient):
        """Testa login com dados vazios"""
        response = client.post("/api/auth/token", 
                              data={"username": "", "password": ""})
        assert response.status_code == 401  # Authentication error 