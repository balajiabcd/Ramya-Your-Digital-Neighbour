"""
Tests for src/routes/health.py
"""

import pytest
import json


class TestHealthRoutes:
    """Test health check endpoints."""
    
    def test_health_endpoint(self, client):
        """Test /health endpoint returns 200."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_liveness_endpoint(self, client):
        """Test /health/live endpoint."""
        response = client.get('/health/live')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'alive'
    
    def test_readiness_endpoint(self, client):
        """Test /health/ready endpoint."""
        response = client.get('/health/ready')
        assert response.status_code in [200, 503]
    
    def test_status_endpoint(self, client):
        """Test /health/status endpoint."""
        response = client.get('/health/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'application' in data
        assert 'system' in data
    
    def test_metrics_endpoint(self, client):
        """Test /metrics endpoint."""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert b'http_requests_total' in response.data
    
    def test_health_includes_timestamp(self, client):
        """Test health endpoint includes timestamp."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'timestamp' in data
