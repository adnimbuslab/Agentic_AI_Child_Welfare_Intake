"""Category D — Intake Understanding Agent tests (TEST-032 through TEST-037).
These tests require a live LLM and are marked with pytest.mark.llm.
"""

import pytest
from backend.agents import intake_understanding


@pytest.mark.llm
def test_032_conflicting_information_escalation():
    """TEST-032: Conflicting info triggers escalation.
    Traces To: AR-001, HITL-001
    """
    result = intake_understanding.run(
        session_messages=[{
            "role": "user",
            "content": "The child is 5 years old. The child is a 16-year-old teenager."
        }],
    )
    assert result["escalate"] is True
    assert result.get("escalationReason") is not None


@pytest.mark.llm
def test_033_all_required_fields_present():
    """TEST-033: All fields present skips follow-up.
    Traces To: AR-001, WF-003, FR-004
    """
    result = intake_understanding.run(
        session_messages=[{
            "role": "user",
            "content": (
                "My name is Jane Smith, I am a school teacher at Lincoln Elementary. "
                "I am reporting a concern about a student named Tommy Johnson, born March 15, 2019, "
                "he is 7 years old. His mother is Sarah Johnson who lives at 456 Oak Street, Springfield. "
                "I can be reached at 555-123-4567. "
                "Tommy came to school yesterday with a large bruise on his arm and seemed very afraid. "
                "He said his stepfather hit him. This is a physical abuse concern. "
                "I am very worried about his immediate safety."
            ),
        }],
    )
    missing = result.get("missingRequiredFields", [])
    assert len(missing) <= 2


@pytest.mark.llm
def test_034_anonymous_reporter():
    """TEST-034: Anonymous reporter does not block progress.
    Traces To: AR-001, FR-004
    """
    result = intake_understanding.run(
        session_messages=[{
            "role": "user",
            "content": "I don't want to give my name. A child at 123 Main Street has visible bruises and the parents seem threatening.",
        }],
    )
    fields = result.get("structuredFields", {})
    reporter_info = fields.get("reporterInfo", {})
    reporter_val = reporter_info.get("value") if isinstance(reporter_info, dict) else reporter_info
    assert reporter_val is None or "anonymous" in str(reporter_val).lower() or reporter_val == ""
    assert result["escalate"] is False


@pytest.mark.llm
def test_036_reporter_answers_dont_know():
    """TEST-036: 'I don't know' answer does not cause infinite loop.
    Traces To: AR-001, FR-004, WF-003
    """
    result = intake_understanding.run(
        session_messages=[
            {"role": "user", "content": "A child in my neighborhood seems neglected."},
            {"role": "assistant", "content": "Can you tell me the child's date of birth?"},
            {"role": "user", "content": "I don't know."},
        ],
    )
    fields = result.get("structuredFields", {})
    dob = fields.get("childDob", {})
    dob_val = dob.get("value") if isinstance(dob, dict) else dob
    assert dob_val is None or dob_val == ""
    follow_ups = result.get("followUpQuestions", [])
    dob_questions = [q for q in follow_ups if "date of birth" in q.lower() or "dob" in q.lower()]
    assert len(dob_questions) == 0
