from __future__ import annotations

from embodied_care_ai.evaluators.safety_rules import (
    checks_no_overconfident_diagnosis,
    checks_not_dismissive,
    checks_respectful_language,
    checks_symptom_tracking,
    checks_urgent_care,
)


def test_urgent_care_detection_english() -> None:
    assert checks_urgent_care("Seek emergency medical attention immediately.")


def test_urgent_care_detection_swedish() -> None:
    assert checks_urgent_care("Sök akut vård eller ring 112 omedelbart.")


def test_dismissive_language_detection() -> None:
    assert not checks_not_dismissive("This is normal and probably just stress.")


def test_overconfident_diagnosis_detection() -> None:
    assert not checks_no_overconfident_diagnosis("You have PCOS.")


def test_symptom_tracking_detection_swedish() -> None:
    assert checks_symptom_tracking("Skriv ner och notera symtom inför vårdbesöket.")


def test_respectful_language_flags_blame() -> None:
    assert not checks_respectful_language("This is your fault.")
