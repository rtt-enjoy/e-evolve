"""
Smoke test for the public earnings digest writer.

The bot's only earnings number that cannot be faked is the on-chain wallet
balance. Everything else in docs/earnings-public.json is a derived view of it.
A change that breaks the derivation path would silently start reporting zero,
and the dashboard would show a healthy project that has stopped earning --
the same shape as a project that has never earned. This test catches the
shape so the regression is visible at review time.
"""
from __future__ import annotations

import json
from pathlib import Path

from bot.earning import status_digest


def test_write_creates_file_with_required_fields(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	status = {
		"wallet": {
			"received_total_usd": 12.5,
			"confirmed_usd": 11.0,
			"last_received_usd": 1.5,
			"last_received_at": "2026-09-05T18:00:00+00:00",
		},
		"earnings": {
			"total_usd": 12.5,
			"confirmed_usd": 11.0,
			"this_week_usd": 1.5,
			"week_started": "2026-08-31",
			"breakdown": {
				"dev.to": 1.5,
				"code_techs": 0.0,
				"mrr-ideas": 0.0,
				"dev.to-newsletter": 0.0,
			},
		},
	}
	status_digest.write(status)
	out = Path("docs/earnings-public.json")
	assert out.exists(), "digest file should be created"
	data = json.loads(out.read_text())
	assert data["lifetime_usd"] == 12.5
	assert data["last_received_usd"] == 1.5
	assert data["breakdown"]["dev.to"] == 1.5
	# Unrecognised breakdown keys are dropped, not echoed back.
	assert "mrr-ideas" in data["breakdown"]


def test_write_is_noop_when_inputs_unchanged(tmp_path, monkeypatch):
	monkeypatch.chdir(tmp_path)
	status = {
		"wallet": {"received_total_usd": 0.0},
		"earnings": {
			"total_usd": 0.0,
			"breakdown": {"dev.to": 0.0, "code_techs": 0.0, "mrr-ideas": 0.0, "dev.to-newsletter": 0.0},
		},
	}
	status_digest.write(status)
	first = Path("docs/earnings-public.json").read_text()
	status_digest.write(status)
	second = Path("docs/earnings-public.json").read_text()
	assert first == second