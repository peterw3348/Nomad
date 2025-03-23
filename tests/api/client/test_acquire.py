"""Unit tests for the api > client > test acquire."""

import requests
from unittest.mock import patch, MagicMock
from src.api.client.acquire import get_credentials, get_process, get_puuid


@patch("subprocess.run")
def test_get_process_success(mock_subprocess_run):
    """Test successful retrieval of port and password from LeagueClientUx process."""
    mock_subprocess_run.return_value.stdout = (
        "--app-port=12345 --remoting-auth-token=testpassword"
    )

    port, password = get_process()

    assert port == "12345"
    assert password == "testpassword"


@patch("subprocess.run")
def test_get_process_no_output(mock_subprocess_run):
    """Test get_process when LeagueClientUx is not running."""
    mock_subprocess_run.return_value.stdout = ""

    port, password = get_process()

    assert port is None
    assert password is None


@patch("subprocess.run")
def test_get_process_missing_credentials(mock_subprocess_run):
    """Test get_process when output does not contain credentials."""
    mock_subprocess_run.return_value.stdout = "--some-other-flag=value"

    port, password = get_process()

    assert port is None
    assert password is None


@patch("src.api.client.acquire.get_process", return_value=("12345", "testpassword"))
@patch("requests.get")
def test_get_puuid_success(mock_requests_get, mock_get_process):
    """Test successful retrieval of PUUID from the League Client API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"puuid": "test-puuid"}
    mock_requests_get.return_value = mock_response

    puuid = get_puuid()

    assert puuid == "test-puuid"


@patch("src.api.client.acquire.get_process", return_value=("12345", "testpassword"))
@patch("requests.get")
def test_get_puuid_request_error(mock_requests_get, mock_get_process):
    """Test get_puuid when the request to the League Client API fails."""
    mock_requests_get.side_effect = requests.RequestException("Connection error")

    puuid = get_puuid()

    assert puuid is None


@patch("src.api.client.acquire.get_process", return_value=(None, None))
def test_get_puuid_missing_credentials(mock_get_process):
    """Test get_puuid when credentials cannot be retrieved."""
    puuid = get_puuid()

    assert puuid is None


@patch("src.api.client.acquire.get_process", return_value=("12345", "testpassword"))
@patch("src.api.client.acquire.get_puuid", return_value="test-puuid")
def test_get_credentials_success(mock_get_puuid, mock_get_process):
    """Test successful retrieval of credentials."""
    port, password, puuid = get_credentials()

    assert port == "12345"
    assert password == "testpassword"
    assert puuid == "test-puuid"


@patch("src.api.client.acquire.get_process", return_value=(None, None))
def test_get_credentials_missing_process(mock_get_process):
    """Test get_credentials when process credentials cannot be retrieved."""
    port, password, puuid = get_credentials()

    assert port is None
    assert password is None
    assert puuid is None
