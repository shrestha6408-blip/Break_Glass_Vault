def classify_obligation(item: dict) -> str:
    """
    Rule-based fallback + structured LLM prompt contract for Freeze / Keep Running / Claim.
    Swap in Claude API structured output in production while preserving this schema.
    """
    category = (item.get("category") or "").lower()
    if category in {"cloud_server", "subscription", "saas"}:
        return "FREEZE_CANCEL_IMMEDIATELY"
    if category in {"utility", "health_insurance", "rent", "emi"}:
        return "KEEP_RUNNING_TEMPORARILY"
    return "CLAIM_OR_HANDOVER"


def build_draft_notice(item: dict, bucket: str) -> dict:
    provider = item.get("provider", "Provider")
    ref_id = item.get("reference_id", "N/A")
    amount = item.get("amount", "N/A")
    due_date = item.get("due_date", "Upcoming")

    if bucket == "FREEZE_CANCEL_IMMEDIATELY":
        subject = f"Urgent Cancellation / Pause Request — {provider} (Ref: {ref_id})"
        body = (
            f"Hello {provider} Support,\n\n"
            f"Please pause or cancel recurring billing for account/reference {ref_id} "
            f"(listed renewal amount: {amount}, next date: {due_date}) due to a family emergency.\n"
            f"Please confirm no further charges will be processed.\n\nRegards,\nDesignated Nominee"
        )
        horizon = "Day 1"
    elif bucket == "KEEP_RUNNING_TEMPORARILY":
        subject = f"Continuity Check & Billing Notice — {provider} (Ref: {ref_id})"
        body = (
            f"Hello {provider} Team,\n\n"
            f"This is an update regarding essential ongoing service {ref_id} ({amount}, due {due_date}). "
            f"Please share current payment status and required nominee contact steps so service is not interrupted.\n\n"
            f"Regards,\nDesignated Nominee"
        )
        horizon = "Day 1–Week 1"
    else:
        subject = f"Emergency Policy / Account Handover Inquiry — {provider} (Ref: {ref_id})"
        body = (
            f"Hello {provider} Claims / Nominee Desk,\n\n"
            f"I am reaching out as a designated contact/nominee regarding policy or account {ref_id}. "
            f"Please provide the exact claim/handover checklist and required documentation.\n\n"
            f"Regards,\nDesignated Nominee"
        )
        horizon = "Week 1–Month 1"

    return {
        "horizon": horizon,
        "subject": subject,
        "body": body,
        "requires_human_approval": True,
    }
