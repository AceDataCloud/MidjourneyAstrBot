"""Midjourney imagine request and terminal-result boundaries."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import MidjourneyClient, MidjourneyError


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = {"x-trace-id": "trace-midjourney"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


@pytest.mark.asyncio
async def test_submit_sends_one_async_imagine_request():
    calls = []

    def fake_open(request, timeout):
        calls.append((request.full_url, json.loads(request.data), timeout))
        return FakeResponse({"task_id": "task-123"})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await MidjourneyClient("test-key").submit("A ceramic vase")
    assert calls == [
        (
            "https://api.acedata.cloud/midjourney/imagine",
            {
                "action": "generate",
                "prompt": "A ceramic vase",
                "mode": "fast",
                "version": "8.1",
                "hd": False,
                "translation": False,
                "split_images": False,
                "async": True,
            },
            90,
        )
    ]
    assert result["status"] == "submitted"
    assert result["task_id"] == "task-123"
    assert "image_url" not in result


@pytest.mark.asyncio
async def test_task_lookup_withholds_preview_and_internal_fields():
    pending = {"id": "task-123", "finished_at": None, "response": None}
    preview = {
        "finished_at": None,
        "response": {
            "success": True,
            "image_url": "https://cdn.example.org/preview.png",
        },
    }
    finished = {
        "finished_at": 123.0,
        "response": {
            "success": True,
            "image_url": "https://cdn.example.org/final.png",
            "sub_image_urls": [
                "https://cdn.example.org/one.png",
                "http://cdn.example.org/unsafe.png",
            ],
            "image_id": "image-456",
            "image_width": 1024,
            "image_height": 1024,
            "cost": {
                "amount": 0.1944,
                "list_amount": 0.216,
                "currency": "credit",
                "supplier": "internal-only",
            },
        },
    }
    with patch(
        "client.OPENER.open",
        side_effect=[
            FakeResponse(pending),
            FakeResponse(preview),
            FakeResponse(finished),
        ],
    ) as opening:
        first = await MidjourneyClient("test-key").query("task-123")
        second = await MidjourneyClient("test-key").query("task-123")
        last = await MidjourneyClient("test-key").query("task-123")
    assert opening.call_count == 3
    assert first["status"] == second["status"] == "pending"
    assert first["image_url"] == second["image_url"] == ""
    assert last["status"] == "succeeded"
    assert last["image_url"] == "https://cdn.example.org/final.png"
    assert last["sub_image_urls"] == ["https://cdn.example.org/one.png"]
    assert last["image_id"] == "image-456"
    assert last["cost"] == {
        "amount": 0.1944,
        "list_amount": 0.216,
        "currency": "credit",
    }
    assert "supplier" not in str(last)


@pytest.mark.asyncio
async def test_invalid_inputs_never_submit_a_paid_job():
    client = MidjourneyClient("test-key")
    for kwargs in (
        {"prompt": " "},
        {"prompt": "A vase", "version": "unknown"},
        {"prompt": "A vase", "split_images": "yes"},
        {"prompt": "A vase --v 8", "version": "8.1"},
        {"prompt": "A vase --sref 12345"},
    ):
        with patch("client.OPENER.open") as opening, pytest.raises(MidjourneyError):
            await client.submit(**kwargs)
        assert opening.call_count == 0
