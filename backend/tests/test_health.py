import pytest
from fastapi.testclient import TestClient

class TestHealthAPI:
    """Testes para os endpoints de health check"""
    
    def test_root_endpoint(self, client: TestClient):
        """Testa o endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "TaleonTracker API"
    
    def test_health_check_endpoint(self, client: TestClient):
        """Testa o endpoint de health check"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_api_endpoints_accessible(self, client: TestClient):
        """Testa se os endpoints da API estão acessíveis"""
        # Testar endpoint de personagens
        response = client.get("/api/characters/")
        assert response.status_code in [200, 404]  # 200 se há dados, 404 se vazio
        
        # Testar endpoint de autenticação (deve retornar 405 para GET)
        response = client.get("/api/auth/token")
        assert response.status_code == 405  # Method not allowed 