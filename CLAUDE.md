# Research Agent Tracker

**Owner:** Bromo (Ben Breaux)
**Current Phase:** Phase 1 — Research Depth Overhaul
**Status:** Active

## Phase 1 Goals (In Progress)
- Increase `max_results` to 10 and set `search_depth="advanced"`.
- Implement a planning step (Claude writes search plan first).
- Implement a reflection step ("is this answer good enough?").
- Implement multi-query expansion (3-5 search angles per task).
- Add a quality bar to the system prompt.
- **Phase 3:** Human-Like Browser Capability (Playwright)
## Future Roadmap (Big Picture)
- Autonomous Code Editing: Allow agent to patch `agent.py` based on errors.
- Browser Automation: Playwright for active platform testing/debug.
- Two-Way Interaction: Real-time SMS via Twilio.

## Deferred Phases
- **Phase 2:** Self-Learning Memory (SQLite)
- **Phase 4:** Two-Way Communication (Twilio SMS / Railway Deploy)