"""
Tests unitaires pour le service VirusTotal.
Les appels réseau sont mockés — aucune connexion internet requise.
"""
import os
from unittest.mock import MagicMock, patch

import pytest

from app.services.virustotal import VirusTotalError, scan_file


@pytest.fixture
def temp_file(tmp_path):
    """Crée un fichier temporaire pour les tests de scan."""
    f = tmp_path / "test_image.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR fake image content")
    return str(f)


def _make_post_response(analysis_id="test-analysis-id-123"):
    mock = MagicMock()
    mock.json.return_value = {"data": {"id": analysis_id}}
    mock.raise_for_status.return_value = None
    return mock


def _make_get_response(malicious=0, suspicious=0, status="completed"):
    mock = MagicMock()
    mock.json.return_value = {
        "data": {
            "attributes": {
                "status": status,
                "stats": {"malicious": malicious, "suspicious": suspicious, "undetected": 10},
            }
        }
    }
    mock.raise_for_status.return_value = None
    return mock


# ── Pas de clé API : scan ignoré ────────────────────────────────────────────

def test_no_api_key_skips_scan(app, temp_file):
    """Sans clé API configurée, le scan doit être ignoré silencieusement."""
    original_key = app.config.get("VIRUSTOTAL_API_KEY")
    app.config["VIRUSTOTAL_API_KEY"] = ""
    try:
        scan_file(temp_file)  # Ne doit pas lever d'exception
    finally:
        app.config["VIRUSTOTAL_API_KEY"] = original_key


# ── Fichier sain ─────────────────────────────────────────────────────────────

@patch("time.sleep")
@patch("app.services.virustotal.requests.get")
@patch("app.services.virustotal.requests.post")
def test_clean_file_passes(mock_post, mock_get, mock_sleep, app, temp_file):
    """Un fichier sain doit passer le scan sans erreur."""
    app.config["VIRUSTOTAL_API_KEY"] = "fake-api-key"
    mock_post.return_value = _make_post_response()
    mock_get.return_value = _make_get_response(malicious=0, suspicious=0)

    try:
        scan_file(temp_file)  # Doit retourner sans exception
    finally:
        app.config["VIRUSTOTAL_API_KEY"] = ""

    mock_post.assert_called_once()
    mock_get.assert_called_once()


# ── Fichier malveillant ───────────────────────────────────────────────────────

@patch("time.sleep")
@patch("app.services.virustotal.requests.get")
@patch("app.services.virustotal.requests.post")
def test_malicious_file_raises_error(mock_post, mock_get, mock_sleep, app, temp_file):
    """Un fichier malveillant doit lever VirusTotalError."""
    app.config["VIRUSTOTAL_API_KEY"] = "fake-api-key"
    mock_post.return_value = _make_post_response()
    mock_get.return_value = _make_get_response(malicious=5, suspicious=0)

    try:
        with pytest.raises(VirusTotalError) as exc_info:
            scan_file(temp_file)
        assert "dangereux" in str(exc_info.value).lower() or \
               "malveillant" in str(exc_info.value).lower() or \
               "identifié" in str(exc_info.value).lower()
    finally:
        app.config["VIRUSTOTAL_API_KEY"] = ""


@patch("time.sleep")
@patch("app.services.virustotal.requests.get")
@patch("app.services.virustotal.requests.post")
def test_suspicious_file_raises_error(mock_post, mock_get, mock_sleep, app, temp_file):
    """Un fichier suspect doit aussi lever VirusTotalError."""
    app.config["VIRUSTOTAL_API_KEY"] = "fake-api-key"
    mock_post.return_value = _make_post_response()
    mock_get.return_value = _make_get_response(malicious=0, suspicious=3)

    try:
        with pytest.raises(VirusTotalError):
            scan_file(temp_file)
    finally:
        app.config["VIRUSTOTAL_API_KEY"] = ""


# ── Erreur réseau lors de l'upload ───────────────────────────────────────────

@patch("app.services.virustotal.requests.post")
def test_upload_network_error_raises(mock_post, app, temp_file):
    """Une erreur réseau lors de l'upload doit lever VirusTotalError."""
    import requests as req
    app.config["VIRUSTOTAL_API_KEY"] = "fake-api-key"
    mock_post.side_effect = req.RequestException("Connexion refusée")

    try:
        with pytest.raises(VirusTotalError) as exc_info:
            scan_file(temp_file)
        assert "indisponible" in str(exc_info.value).lower()
    finally:
        app.config["VIRUSTOTAL_API_KEY"] = ""


# ── Timeout (analyse jamais terminée) ────────────────────────────────────────

@patch("time.sleep")
@patch("app.services.virustotal.requests.get")
@patch("app.services.virustotal.requests.post")
def test_timeout_raises_error(mock_post, mock_get, mock_sleep, app, temp_file):
    """Si l'analyse ne se termine jamais, VirusTotalError doit être levée."""
    app.config["VIRUSTOTAL_API_KEY"] = "fake-api-key"
    mock_post.return_value = _make_post_response()
    # L'analyse reste toujours en cours "queued"
    mock_get.return_value = _make_get_response(status="queued")

    try:
        with pytest.raises(VirusTotalError) as exc_info:
            scan_file(temp_file)
        assert "indisponible" in str(exc_info.value).lower()
    finally:
        app.config["VIRUSTOTAL_API_KEY"] = ""
