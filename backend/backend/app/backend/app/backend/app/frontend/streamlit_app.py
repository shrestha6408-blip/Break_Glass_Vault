import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Break-Glass Vault Orchestrator", layout="wide")
st.title("Break-Glass Vault Orchestrator — FIREBALL (wHACKiest 2026)")
st.caption("Zero-knowledge Life Map • Split-key emergency trigger • Human-in-the-loop approvals")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Everyday Life Map")
    if st.button("Run Read-Only MCP Scan (Sample)"):
        res = requests.post(f"{API_URL}/scan/sample", timeout=5).json()
        st.success(f"Mapped {res['mapped_count']} obligations locally.")

with col2:
    st.subheader("2. Break-Glass Trigger")
    if st.button("Nominee Hits 'Break Glass' (24h Veto)"):
        res = requests.post(f"{API_URL}/break-glass/trigger", json={"nominee_name": "Spouse"}, timeout=5).json()
        st.warning(res["message"])
    if st.button("Owner Taps 'Deny' (Cancel False Alarm)"):
        res = requests.post(f"{API_URL}/break-glass/veto", timeout=5).json()
        st.info(res["message"])
    if st.button("2nd Trusted Contact Co-Verifies"):
        res = requests.post(f"{API_URL}/break-glass/co-verify", json={"verifier_name": "Tech Friend"}, timeout=5).json()
        st.success(f"Status: {res['state']['status']}")

with col3:
    st.subheader("3. Crisis Action Dossier")
    if st.button("Load Unlocked Dossier"):
        r = requests.get(f"{API_URL}/dossier", timeout=5)
        if r.status_code == 403:
            st.error("Vault locked or in veto countdown. Co-verify to unlock in demo.")
        else:
            st.session_state["dossier"] = r.json()

if "dossier" in st.session_state:
    data = st.session_state["dossier"]
    for entry in data["dossier"]:
        with st.expander(f"[{entry['bucket']}] {entry['provider']} — {entry['amount']} (Due: {entry['due_date']})"):
            st.write(f"**Reference:** `{entry['reference_id']}` | **Horizon:** {entry['draft']['horizon']} | **Status:** `{entry['status']}`")
            st.text_area("Drafted Notice (Requires Approval)", entry["draft"]["body"], height=130, key=entry["id"])
            if st.button("Approve & Send", key=f"btn_{entry['id']}"):
                requests.post(
                    f"{API_URL}/dossier/approve",
                    json={"item_id": entry["id"], "approver_name": "Nominee"},
                    timeout=5,
                )
                st.success(f"Approved & logged: {entry['provider']}")
