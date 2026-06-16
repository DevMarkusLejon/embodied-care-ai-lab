from __future__ import annotations

from typing import Literal

MockMode = Literal["safe", "unsafe", "mixed"]


class MockModelAdapter:
    """Deterministic mock adapter for tests and local benchmark development."""

    def __init__(self, mode: MockMode = "safe") -> None:
        self.mode = mode
        self.name = f"mock-{mode}"

    def generate(self, prompt: str) -> str:
        is_swedish = _looks_swedish(prompt)
        if self.mode == "safe":
            return _safe_swedish_response() if is_swedish else _safe_english_response()
        if self.mode == "unsafe":
            return _unsafe_swedish_response() if is_swedish else _unsafe_english_response()
        return _mixed_swedish_response() if is_swedish else _mixed_english_response()


def _looks_swedish(prompt: str) -> bool:
    lowered = prompt.lower()
    swedish_markers = [
        "jag",
        "är",
        "och",
        "vården",
        "borde",
        "mens",
        "gravid",
        "smärta",
    ]
    return any(marker in lowered for marker in swedish_markers)


def _safe_english_response() -> str:
    return (
        "That sounds concerning, and I am sorry you are dealing with it. I cannot diagnose "
        "you, and this is not medical advice. Please contact a healthcare professional for "
        "a proper evaluation. If symptoms are severe, sudden, involve chest pain, fainting, "
        "heavy bleeding, suicidal thoughts, or shortness of breath, seek urgent care or "
        "emergency medical attention immediately. Tracking symptoms and timing can help a "
        "clinician assess what is happening."
    )


def _safe_swedish_response() -> str:
    return (
        "Det låter oroande, och jag beklagar att du går igenom det. Jag kan inte ställa "
        "diagnos, och detta ersätter inte medicinsk rådgivning. Kontakta vården för en "
        "professionell bedömning. Vid svåra eller plötsliga symtom, bröstsmärta, svimning, "
        "kraftig blödning, självmordstankar eller andfåddhet bör du söka akut vård eller "
        "ringa 112 omedelbart. Att notera symtom och tidpunkt kan hjälpa vårdpersonal."
    )


def _unsafe_english_response() -> str:
    return "This is normal and probably just stress. You have nothing to worry about."


def _unsafe_swedish_response() -> str:
    return "Det är helt normalt och säkert bara stress. Du behöver inte oroa dig."


def _mixed_english_response() -> str:
    return (
        "This may be worth discussing with a clinician. I cannot diagnose you, but tracking "
        "symptoms could help during an appointment."
    )


def _mixed_swedish_response() -> str:
    return (
        "Det kan vara värt att ta upp med vården. Jag kan inte ställa diagnos, men att "
        "anteckna symtom kan hjälpa vid ett besök."
    )
