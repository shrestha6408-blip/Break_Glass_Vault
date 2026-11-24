# Break-Glass Vault 

**Team:** FIREBALL | **College:** Ramaiah Institute of Technology  
**Event:** wHACKiest 2026 Online Ideathon (26–27 Nov 2026)  
**Track:** Make MCP Matter – AI Agents for Everyday Life[cite: 3, 4]  
**Team Members:**
* **Shrestha Bhadra** (Lead) — `1MS25ET049`
* **Purnima Meachery** — `1MS25ET033`

---

## Overview

When a person is suddenly hospitalized, incapacitated, or passes away, families are often left untangling scattered financial accounts, insurance policies, subscriptions, renewals, and autopays during an emotional crisis[cite: 4]. Existing tools fall short: spreadsheets go stale, password managers store raw credentials without operational context, and static digital wills rarely guide immediate triage[cite: 4].

**Break-Glass Vault Orchestrator** is a local-first AI agent powered by **Model Context Protocol (MCP)** that quietly builds a zero-knowledge **Life Map** of everyday obligations and unlocks a human-approved **Crisis Action Dossier** only when a verified emergency trigger fires[cite: 4].

---

## Key Capabilities

* **Zero-Knowledge Everyday Life Map:** Connects via read-only MCP servers (Gmail/IMAP, Google Calendar, Local Filesystem) to spot recurring obligations and store metadata only—never raw passwords or bank PINs[cite: 4].
* **Trusted Circle & Split-Key Vault:** Assigns role-based nominees and protects local encrypted SQLite storage using **AES** encryption and **Shamir's Secret Sharing** so no single party can unlock data unilaterally during normal life[cite: 4].
* **Break-Glass Trigger & False-Alarm Guards:** Supports inactivity check-ins (dead-man's switch) and nominee-initiated break-glass requests with a **24–48 hour owner veto window** and **two-contact co-verification**[cite: 4].
* **Triage & Action Dossier:** Classifies obligations into **Freeze / Cancel Immediately**, **Keep Running Temporarily**, or **Claim / Handover**, builds a Day 1 / Week 1 / Month 1 plan, and drafts claim/cancellation notices[cite: 4].
* **Human-in-the-Loop Execution:** The agent never spends money, deletes accounts, or sends messages autonomously—nominees review drafts, click **Approve & Send**, and track actions in an audit log[cite: 4].

---

## Architecture & Tech Stack

* **MCP Connectors (Input):** Read-only bridges for Gmail/IMAP (statements/receipts), Google Calendar (renewal dates), and Local Filesystem (policy/document PDFs)[cite: 4].
* **Backend & Scheduling:** Python + FastAPI + APScheduler (for periodic scans and check-in timers)[cite: 4].
* **Security & Storage:** Local SQLite + AES encryption + Shamir's Secret Sharing + append-only audit log[cite: 4].
* **AI Orchestration:** LLM classifier and notice drafter (structured outputs with human approval gates)[cite: 4].
* **Frontend:** Streamlit / React nominee dashboard (`Review Draft`, `View Documents`, `Mark Complete`, `Approve & Send`)[cite: 4].

---

## Quickstart (Local Demo)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
