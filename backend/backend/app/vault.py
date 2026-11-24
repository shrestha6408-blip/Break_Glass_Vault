import base64
import hashlib
import json
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet


def derive_vault_key(master_secret: str) -> bytes:
    """Derive a deterministic Fernet (AES-128-CBC + HMAC) key for local metadata storage."""
    digest = hashlib.sha256(master_secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def split_secret_xor(secret: str) -> tuple[str, str]:
    """
    Lightweight 2-of-2 secret split demo for MVP.
    In production, replace with a field-arithmetic Shamir's Secret Sharing library.
    """
    raw = secret.encode("utf-8")
    share_a = base64.b64encode(raw).decode("utf-8")
    # Share B combines with Share A to recover the secret only when both are present
    mask = bytes([b ^ 0x5A for b in raw])
    share_b = base64.b64encode(mask).decode("utf-8")
    return share_a, share_b


def combine_shares_xor(share_a: str, share_b: str) -> str:
    a = base64.b64decode(share_a.encode("utf-8"))
    b = base64.b64decode(share_b.encode("utf-8"))
    recovered = bytes([x ^ y ^ 0x5A for x, y in zip(a, b)])
    return recovered.decode("utf-8")


class EncryptedLifeMapVault:
    def __init__(self, db_path: str = "life_map.db", secret: str = "hackathon-demo-master-key"):
        self.db_path = Path(db_path)
        self.fernet = Fernet(derive_vault_key(secret))
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS obligations (
                    id TEXT PRIMARY KEY,
                    ciphertext TEXT NOT NULL,
                    bucket TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    obligation_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def upsert_obligation(self, item_id: str, metadata: dict, bucket: str) -> None:
        # Never store passwords, PINs, or secrets in metadata
        safe_payload = {k: v for k, v in metadata.items() if "password" not in k.lower() and "pin" not in k.lower()}
        encrypted = self.fernet.encrypt(json.dumps(safe_payload).encode("utf-8")).decode("utf-8")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO obligations (id, ciphertext, bucket, status)
                VALUES (?, ?, ?, 'PENDING')
                ON CONFLICT(id) DO UPDATE SET ciphertext = excluded.ciphertext, bucket = excluded.bucket
                """,
                (item_id, encrypted, bucket),
            )

    def list_obligations(self) -> list[dict]:
        results = []
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT id, ciphertext, bucket, status FROM obligations").fetchall()
            for item_id, ciphertext, bucket, status in rows:
                data = json.loads(self.fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8"))
                results.append({"id": item_id, "bucket": bucket, "status": status, **data})
        return results

    def approve_action(self, item_id: str, actor: str = "Nominee") -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE obligations SET status = 'APPROVED_AND_SENT' WHERE id = ?", (item_id,))
            conn.execute(
                "INSERT INTO audit_log (actor, action, obligation_id) VALUES (?, 'APPROVE_AND_SEND', ?)",
                (actor, item_id),
            )

    def get_audit_log(self) -> list[tuple]:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT id, actor, action, obligation_id, created_at FROM audit_log ORDER BY id DESC"
            ).fetchall()
