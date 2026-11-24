from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.classifier import build_draft_notice, classify_obligation
from app.vault import EncryptedLifeMapVault

app = FastAPI(title="Break-Glass Vault Orchestrator API")
vault = EncryptedLifeMapVault()

# Simulated break-glass state for MVP demo
trigger_state = {
    "status": "LOCKED",  # LOCKED | VETO_WINDOW_ACTIVE | UNLOCKED
    "veto_expires_at": None,
    "co_verifications": [],
}


class BreakGlassRequest(BaseModel):
    nominee_name: str
    reason: str = "Sudden hospitalization"
    veto_hours: int = 24


class CoVerifyRequest(BaseModel):
    verifier_name: str


class ApprovalRequest(BaseModel):
    item_id: str
    approver_name: str


@app.post("/scan/sample")
def run_sample_mcp_scan():
    sample_items = [
        {
            "id": "obl-1",
            "provider": "AWS Cloud / Prod Server",
            "category": "cloud_server",
            "reference_id": "ACCT-9921",
            "amount": "₹40,000/yr",
            "due_date": "In 3 days",
            "source": "MCP:Gmail+Calendar",
        },
        {
            "id": "obl-2",
            "provider": "BESCOM Home Electricity & Family Health",
            "category": "utility",
            "reference_id": "CA-774120",
            "amount": "₹3,450/mo",
            "due_date": "In 5 days",
            "source": "MCP:Gmail",
        },
        {
            "id": "obl-3",
            "provider": "HDFC Life Term Policy",
            "category": "insurance",
            "reference_id": "POL-HDFC-88312",
            "amount": "₹1.5 Cr Sum Assured",
            "due_date": "Annual",
            "source": "MCP:LocalDocs",
        },
    ]
    for item in sample_items:
        bucket = classify_obligation(item)
        vault.upsert_obligation(item["id"], item, bucket)
    return {"mapped_count": len(sample_items), "obligations": vault.list_obligations()}


@app.post("/break-glass/trigger")
def trigger_break_glass(req: BreakGlassRequest):
    expires = datetime.now(timezone.utc) + timedelta(hours=req.veto_hours)
    trigger_state["status"] = "VETO_WINDOW_ACTIVE"
    trigger_state["veto_expires_at"] = expires.isoformat()
    trigger_state["co_verifications"] = [req.nominee_name]
    return {"message": "24-48h owner veto countdown started", "state": trigger_state}


@app.post("/break-glass/veto")
def owner_veto():
    trigger_state["status"] = "LOCKED"
    trigger_state["veto_expires_at"] = None
    trigger_state["co_verifications"] = []
    return {"message": "Owner tapped Deny; vault remains locked", "state": trigger_state}


@app.post("/break-glass/co-verify")
def co_verify(req: CoVerifyRequest):
    if req.verifier_name not in trigger_state["co_verifications"]:
        trigger_state["co_verifications"].append(req.verifier_name)
    if len(trigger_state["co_verifications"]) >= 2:
        trigger_state["status"] = "UNLOCKED"
    return {"message": "Co-verification recorded", "state": trigger_state}


@app.get("/dossier")
def get_dossier():
    if trigger_state["status"] != "UNLOCKED":
        raise HTTPException(status_code=403, detail="Vault is still locked or inside veto window.")
    items = vault.list_obligations()
    dossier = []
    for item in items:
        draft = build_draft_notice(item, item["bucket"])
        dossier.append({**item, "draft": draft})
    return {"status": "UNLOCKED", "dossier": dossier, "audit_log": vault.get_audit_log()}


@app.post("/dossier/approve")
def approve_dossier_item(req: ApprovalRequest):
    vault.approve_action(req.item_id, actor=req.approver_name)
    return {"ok": True, "audit_log": vault.get_audit_log()}
