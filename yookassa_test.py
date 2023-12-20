import pytest
from unittest.mock import MagicMock, patch
from yookassa_integration import YooKassaIntegration

@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.status_code = 200
    return mock

class TestYooKassaIntegration:
    @pytest.fixture
    def yookassa_integration(self):
        return YooKassaIntegration("your_shop_id", "your_secret_key")

    @pytest.mark.asyncio
    async def test_create_payment_success(self, yookassa_integration, mock_response):
        with patch("yookassa_integration.requests.post", return_value=mock_response):
            result_url, payment_id = yookassa_integration.create_payment(100.0)
            assert result_url is not None
            assert payment_id is not None

    @pytest.mark.asyncio
    async def test_create_payment_failure(self, yookassa_integration, mock_response):
        mock_response.status_code = 500
        with patch("yookassa_integration.requests.post", return_value=mock_response):
            result_url, payment_id = yookassa_integration.create_payment(100.0)
            assert result_url is None
            assert payment_id is None

    @pytest.mark.asyncio
    async def test_check_payment_status_success(self, yookassa_integration, mock_response):
        with patch("yookassa_integration.requests.get", return_value=mock_response):
            payment_status = yookassa_integration.check_payment_status("payment_id")
            assert payment_status is not None

    @pytest.mark.asyncio
    async def test_check_payment_status_failure(self, yookassa_integration, mock_response):
        mock_response.status_code = 500
        with patch("yookassa_integration.requests.get", return_value=mock_response):
            payment_status = yookassa_integration.check_payment_status("payment_id")
            assert payment_status is None

    def test_handle_webhook(self, yookassa_integration):
        sample_data = {
            'object': {
                'id': 'payment_id',
                'status': 'succeeded'
            }
        }
        payment_id, status = yookassa_integration.handle_webhook(sample_data)
        assert payment_id == 'payment_id'
        assert status == 'succeeded'
