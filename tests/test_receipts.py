from datetime import datetime, timezone

from autopilot.src.receipts import build_receipt, write_receipt


def test_receipt_written(tmp_path, monkeypatch):
    monkeypatch.setenv("RECEIPTS_DIR", str(tmp_path))
    receipt = build_receipt(
        run_id="run_123",
        workflow_name="Test",
        status="completed",
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc),
        inputs={"config": {}},
        decisions={},
        actions=[],
        results=[],
        metrics={},
    )
    path = write_receipt(receipt)
    assert path.exists()
