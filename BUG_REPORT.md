# Bug Report Summary

This document summarizes the highest impact issues discovered while running automated patient calls. Each issue includes evidence from transcripts and the scenario context.

## Top issues
1. Looping and runaway responses  
Evidence: reference run folder and turn number  
Impact: conversation does not terminate, degrades patient experience  
Suggested fix: add turn end conditions, detect repeated farewell patterns, stop generation after closure intent

2. Scheduling contradictions  
Evidence: patient requests one time window but agent confirms another  
Impact: appointment workflow fails  
Suggested fix: explicit slot confirmation step and state tracking for requested constraints

3. Medication refill workflow errors  
Evidence: agent requests incorrect information or provides an unrealistic refill process  
Impact: incorrect handling of common patient request  
Suggested fix: enforce refill checklist, ask for medication name, dosage, pharmacy, prescribing provider, confirm policy

4. Low quality or incoherent phrasing  
Evidence: ungrammatical responses, excessive filler  
Impact: trust and professionalism issues  
Suggested fix: style constraints, disfluency filtering, response length limits

## Notes
- Each call run folder contains recordings, transcript, and bug report for full evidence.
- Sensitive information is not committed. Any personal data in transcripts should be redacted before publishing.
