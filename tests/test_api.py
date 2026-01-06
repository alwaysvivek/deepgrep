"""
Comprehensive API tests for DeepGrep web application.
Tests cover regex search, semantic search, and home route endpoints.
"""
import pytest
import json
from deepgrep.web.app import app
from unittest.mock import patch


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    # Disable rate limiting for tests
    app.config['RATELIMIT_ENABLED'] = False
    with app.test_client() as client:
        yield client


class TestHomeRoute:
    """Tests for the home route."""
    
    def test_home_returns_200(self, client):
        """Test that the home route returns status 200."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_home_returns_html(self, client):
        """Test that the home route returns HTML content."""
        response = client.get('/')
        assert b'html' in response.data.lower() or response.content_type == 'text/html; charset=utf-8'


class TestRegexSearchEndpoint:
    """Tests for the /search endpoint (regex matching)."""
    
    def test_regex_search_with_valid_pattern(self, client):
        """Test regex search with a valid pattern that matches."""
        data = {
            "pattern": r"\d+",
            "text": "User logged in at 14:32, error code 404"
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'matches' in json_data
        assert 'history' in json_data
        assert isinstance(json_data['matches'], list)
        assert len(json_data['matches']) > 0
        assert '14' in json_data['matches'] or '32' in json_data['matches']
    
    def test_regex_search_empty_pattern(self, client):
        """Test that empty pattern returns 400 error."""
        data = {
            "pattern": "",
            "text": "Some text here"
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_regex_search_empty_text(self, client):
        """Test that empty text returns 400 error."""
        data = {
            "pattern": r"\d+",
            "text": ""
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_regex_search_missing_pattern(self, client):
        """Test that missing pattern field returns 400 error."""
        data = {
            "text": "Some text here"
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_regex_search_missing_text(self, client):
        """Test that missing text field returns 400 error."""
        data = {
            "pattern": r"\d+"
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_regex_search_complex_email_pattern(self, client):
        """Test complex regex pattern for email matching."""
        data = {
            "pattern": r"\w+@\w+\.\w+",
            "text": "Contact us at support@example.com or admin@test.org"
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'matches' in json_data
        assert len(json_data['matches']) > 0
    
    def test_regex_search_date_pattern(self, client):
        """Test complex regex pattern for date matching."""
        data = {
            "pattern": r"\d{4}-\d{2}-\d{2}",
            "text": "Event dates: 2024-01-15 and 2024-12-31"
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'matches' in json_data
        assert len(json_data['matches']) == 2
    
    def test_regex_search_response_structure(self, client):
        """Test that response has correct structure with matches and history arrays."""
        data = {
            "pattern": r"\w+",
            "text": "hello world"
        }
        response = client.post('/search',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'matches' in json_data
        assert 'history' in json_data
        assert isinstance(json_data['matches'], list)
        assert isinstance(json_data['history'], list)


class TestSemanticSearchEndpoint:
    """Tests for the /semantic endpoint."""
    
    @patch('deepgrep.web.app.semantic_engine')
    def test_semantic_search_with_valid_keyword(self, mock_engine, client):
        """Test semantic search with a valid keyword."""
        # Mock the semantic engine to return predictable results
        mock_engine.find_semantic_matches.return_value = [
            ("joyful", 0.88),
            ("delighted", 0.82)
        ]
        
        data = {
            "keyword": "happy",
            "text": "She felt joyful and delighted after the announcement"
        }
        response = client.post('/semantic',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'matches' in json_data
        assert 'history' in json_data
        assert isinstance(json_data['matches'], list)
        assert len(json_data['matches']) == 2
        
        # Verify match structure
        first_match = json_data['matches'][0]
        assert 'word' in first_match
        assert 'similarity' in first_match
    
    def test_semantic_search_missing_keyword(self, client):
        """Test that missing keyword returns 400 error."""
        data = {
            "text": "Some text here"
        }
        response = client.post('/semantic',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_semantic_search_empty_keyword(self, client):
        """Test that empty keyword returns 400 error."""
        data = {
            "keyword": "",
            "text": "Some text here"
        }
        response = client.post('/semantic',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_semantic_search_missing_text(self, client):
        """Test that missing text returns 400 error."""
        data = {
            "keyword": "happy"
        }
        response = client.post('/semantic',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    def test_semantic_search_empty_text(self, client):
        """Test that empty text returns 400 error."""
        data = {
            "keyword": "happy",
            "text": ""
        }
        response = client.post('/semantic',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('deepgrep.web.app.semantic_engine')
    def test_semantic_search_similarity_scores_present(self, mock_engine, client):
        """Test that similarity scores are present in the response."""
        mock_engine.find_semantic_matches.return_value = [
            ("happy", 0.95),
            ("glad", 0.78)
        ]
        
        data = {
            "keyword": "joyful",
            "text": "I feel happy and glad today"
        }
        response = client.post('/semantic',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        
        for match in json_data['matches']:
            assert 'similarity' in match
            assert isinstance(match['similarity'], (int, float))
            assert 0 <= match['similarity'] <= 1
    
    @patch('deepgrep.web.app.semantic_engine')
    def test_semantic_search_response_structure(self, mock_engine, client):
        """Test that response includes matches with word and similarity fields."""
        mock_engine.find_semantic_matches.return_value = [
            ("excited", 0.85)
        ]
        
        data = {
            "keyword": "happy",
            "text": "I am excited about the news"
        }
        response = client.post('/semantic',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'matches' in json_data
        assert 'history' in json_data
        assert isinstance(json_data['matches'], list)
        
        if len(json_data['matches']) > 0:
            match = json_data['matches'][0]
            assert 'word' in match
            assert 'similarity' in match
