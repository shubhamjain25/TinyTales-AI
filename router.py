from schema import AppState, MAX_REVISIONS

def hitl_router(p_state: AppState):
    """
    Routes to formatter on approval OR when the revision budget is exhausted
    (auto-approves the last generated version rather than looping forever).
    """
    if p_state["status"] == "APPROVED":
        return "APPROVED"

    if p_state["revision_count"] >= MAX_REVISIONS:
        # Budget exhausted — pass whatever we have to the formatter
        return "APPROVED"

    return "NEEDS_REVISION"