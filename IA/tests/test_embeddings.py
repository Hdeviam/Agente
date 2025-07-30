import pytest
import os
from unittest.mock import patch, MagicMock
from app.services.embeddings.bedrock_service import embed_text
from app.services.embeddings.search_opensearch import search_similar_properties

class TestEmbeddingService:
    """Tests para el servicio de embeddings"""

    def test_embed_text_success(self):
        """Test exitoso de generación de embeddings"""
        with patch('app.services.embeddings.bedrock_service.get_embed_client') as mock_client:
            # Mock del cliente Bedrock
            mock_response = {
                'body': MagicMock()
            }
            mock_response['body'].read.return_value = '{"embedding": [0.1, 0.2, 0.3]}'
            mock_client.return_value.invoke_model.return_value = mock_response

            result = embed_text("test property")
            assert result == [0.1, 0.2, 0.3]

    def test_embed_text_error_handling(self):
        """Test manejo de errores en embeddings"""
        with patch('app.services.embeddings.bedrock_service.get_embed_client') as mock_client:
            mock_client.return_value.invoke_model.side_effect = Exception("API Error")

            result = embed_text("test property")
            assert isinstance(result, str)
            assert "ERROR" in result

class TestSearchService:
    """Tests para el servicio de búsqueda"""

    @patch('app.services.embeddings.search_opensearch.get_opensearch_client')
    @patch('app.services.embeddings.search_opensearch.embed_text')
    def test_search_with_filters(self, mock_embed, mock_client):
        """Test búsqueda con filtros"""
        # Mock embedding
        mock_embed.return_value = [0.1, 0.2, 0.3]

        # Mock OpenSearch response
        mock_response = {
            "hits": {
                "hits": [
                    {
                        "_id": "test1",
                        "_score": 0.95,
                        "_source": {
                            "text": "Departamento en Lima",
                            "city": "lima",
                            "property_type": "departamento",
                            "operation_type": "alquiler"
                        }
                    }
                ]
            }
        }
        mock_client.return_value.search.return_value = mock_response

        results = search_similar_properties(
            query="departamento en Lima",
            ciudad="lima",
            property_type="departamento",
            k=3
        )

        assert len(results) == 1
        assert results[0]["city"] == "lima"
        assert results[0]["property_type"] == "departamento"

    @patch('app.services.embeddings.search_opensearch.get_opensearch_client')
    @patch('app.services.embeddings.search_opensearch.embed_text')
    def test_search_error_handling(self, mock_embed, mock_client):
        """Test manejo de errores en búsqueda"""
        mock_embed.return_value = [0.1, 0.2, 0.3]
        mock_client.return_value.search.side_effect = Exception("OpenSearch Error")

        results = search_similar_properties("test query")
        assert results == []

if __name__ == "__main__":
    pytest.main([__file__])
