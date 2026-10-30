"""Insert fictional, clearly labeled demo records for testing the API."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import connection, initialize


def main() -> None:
    initialize()
    with connection() as db:
        existing = db.execute("SELECT id FROM transactions WHERE reference='DEMO-INV-1001'").fetchone()
        if existing:
            print("Demo records already exist; nothing changed.")
            return
        db.execute("INSERT INTO transactions(date,description,amount,currency,supplier,reference,source_row) VALUES(?,?,?,?,?,?,?)",
                   ("2026-01-15", "Demo supplier invoice payment", 1250.00, "USD", "Example Supplies Ltd", "DEMO-INV-1001", 0))
        tx_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.execute("INSERT INTO transactions(date,description,amount,currency,supplier,reference,source_row) VALUES(?,?,?,?,?,?,?)",
                   ("2026-01-16", "Demo second supplier payment", 1250.00, "USD", "Example Supplies Ltd", "DEMO-INV-1002", 0))
        evidence = ["Both demo records name Example Supplies Ltd.", "Both demo records have amount USD 1250.00.", "The recorded dates are one day apart."]
        db.execute("INSERT INTO findings(transaction_id,finding_type,severity,evidence_json) VALUES(?,?,?,?)",
                   (tx_id, "possible_duplicate_payment", "medium", json.dumps(evidence)))
    print("Inserted fictional demo transactions and finding (finding id 1 may differ).")


if __name__ == "__main__":
    main()
