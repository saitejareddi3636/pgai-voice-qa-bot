from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    patient_lines: List[str]


SCENARIOS: Dict[str, Scenario] = {
    "schedule_basic": Scenario(
        name="schedule_basic",
        description="Simple new appointment scheduling",
        patient_lines=[
            "Hi, I want to schedule an appointment.",
            "Next week works. Do you have anything on Tuesday afternoon?",
            "Actually, can we do Wednesday morning instead?",
            "Thanks. That is all.",
        ],
    ),
    "reschedule_cancel": Scenario(
        name="reschedule_cancel",
        description="Reschedule then cancel",
        patient_lines=[
            "Hi, I need to reschedule my appointment.",
            "I cannot make it on Friday. Do you have something next week?",
            "Actually cancel it. I will call back later to book again.",
            "Thank you.",
        ],
    ),
    "refill_standard": Scenario(
        name="refill_standard",
        description="Medication refill request with required details",
        patient_lines=[
            "Hi, I need a medication refill.",
            "The medication is metformin, five hundred milligrams.",
            "My pharmacy is CVS on University Drive. Can you send the refill there?",
            "Thanks, that is all.",
        ],
    ),
    "insurance_hours": Scenario(
        name="insurance_hours",
        description="Ask about office hours and insurance coverage",
        patient_lines=[
            "Hi, what are your office hours this week?",
            "Do you accept Blue Cross Blue Shield?",
            "Where are you located? I need the address.",
            "Thank you.",
        ],
    ),
    "edge_loop_trap": Scenario(
        name="edge_loop_trap",
        description="Try to trigger looping and confusion",
        patient_lines=[
            "Hi, I have a quick question but I keep getting disconnected.",
            "If you did not hear me, I can repeat. Can you confirm you heard my last sentence?",
            "Ok, can you repeat what you think I asked for in your own words?",
            "Thanks, goodbye.",
        ],
    ),
}
