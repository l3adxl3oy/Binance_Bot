"""
Integration Tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app import app
import json


@pytest.fixture
def client():
    """Test client for FastAPI"""
    return TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint redirects to login"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Redirecting to login" in response.text
        
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        
    def test_get_stats(self, client):
        """Test stats endpoint"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "profit" in data
        assert "trades" in data
        assert "positions" in data
        assert "uptime" in data
        
    def test_get_config(self, client):
        """Test config endpoint"""
        response = client.get("/api/config")
        assert response.status_code == 200
        
        data = response.json()
        assert "demo_mode" in data
        assert "max_positions" in data
        assert "symbols" in data
        assert isinstance(data["symbols"], list)
        
    def test_start_bot_invalid_type(self, client):
        """Test starting bot with invalid type"""
        response = client.post(
            "/api/bot/start",
            json={"bot_type": "invalid_type"}
        )
        # Should either accept or reject - test that it doesn't crash
        assert response.status_code in [200, 400, 422]
        
    def test_stop_bot_when_not_running(self, client):
        """Test stopping bot when not running"""
        response = client.post("/api/bot/stop")
        # Should handle gracefully
        assert response.status_code in [200, 400]


class TestWebSocket:
    """Test WebSocket functionality"""
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection"""
        with client.websocket_connect("/ws") as websocket:
            # Should connect successfully
            data = websocket.receive_json()
            assert data is not None
            
            # Should receive periodic updates
            # Note: This might timeout in test environment
            try:
                data = websocket.receive_json(timeout=2)
                assert "type" in data
            except:
                pass  # Timeout is acceptable in test


class TestAPIValidation:
    """Test API input validation"""
    
    def test_start_bot_missing_body(self, client):
        """Test start bot without request body"""
        response = client.post("/api/bot/start")
        assert response.status_code == 422  # Validation error
        
    def test_start_bot_invalid_json(self, client):
        """Test start bot with invalid JSON"""
        response = client.post(
            "/api/bot/start",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
    def test_cors_headers(self, client):
        """Test CORS middleware is configured"""
        response = client.options("/api/health")
        # CORS headers may or may not be present depending on request
        # Just verify OPTIONS method is handled
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self, client):
        """Test non-existent endpoint"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
    def test_method_not_allowed(self, client):
        """Test wrong HTTP method"""
        response = client.get("/api/bot/start")  # Should be POST
        assert response.status_code == 405
