import time
import os

import requests
from flask import current_app


class VirusTotalError(Exception):
    """Levée quand le scan échoue ou que le fichier est rejeté."""
    pass


def scan_file(filepath: str) -> None:
    """
    Scanne un fichier avec l'API VirusTotal v3.
    - Ne fait rien si aucune clé API n'est configurée.
    - Lève VirusTotalError si le fichier est malveillant ou si le service est indisponible.
    """
    api_key = current_app.config.get("VIRUSTOTAL_API_KEY", "")
    if not api_key:
        return  # Pas de clé configurée — scan ignoré

    headers = {"x-apikey": api_key}

    # 1. Upload du fichier vers VirusTotal
    try:
        with open(filepath, "rb") as f:
            response = requests.post(
                "https://www.virustotal.com/api/v3/files",
                headers=headers,
                files={"file": f},
                timeout=30,
            )
        response.raise_for_status()
        analysis_id = response.json()["data"]["id"]
    except requests.RequestException:
        raise VirusTotalError(
            "Le service de vérification est temporairement indisponible. "
            "Veuillez réessayer dans quelques instants."
        )

    # 2. Attente des résultats (max 60 secondes, toutes les 5s)
    for _ in range(12):
        time.sleep(5)
        try:
            result = requests.get(
                f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",
                headers=headers,
                timeout=15,
            )
            result.raise_for_status()
            data = result.json()["data"]

            if data["attributes"]["status"] == "completed":
                stats = data["attributes"]["stats"]
                malicious = stats.get("malicious", 0) + stats.get("suspicious", 0)
                if malicious > 0:
                    raise VirusTotalError(
                        "Ce fichier n'a pas pu être téléchargé car il a été "
                        "identifié comme potentiellement dangereux."
                    )
                return  # Fichier sain

        except VirusTotalError:
            raise  # Propager l'erreur de rejet
        except requests.RequestException:
            raise VirusTotalError(
                "Le service de vérification est temporairement indisponible. "
                "Veuillez réessayer dans quelques instants."
            )

    # Timeout dépassé
    raise VirusTotalError(
        "Le service de vérification est temporairement indisponible. "
        "Veuillez réessayer dans quelques instants."
    )
