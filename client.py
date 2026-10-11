"""Midjourney imagine submission and existing-task lookup for AstrBot."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_BASE = "https://api.acedata.cloud"
VERSIONS = {"8.1", "8", "7", "6.1", "6", "5.2"}
FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}
BILLING_FLAGS = re.compile(
    r"(?<!\S)--(?:v|version|q|quality|sref|p|hd)(?=\s|$)",
    re.IGNORECASE,
)


class _NoRedirect(HTTPRedirectHandler):
    """Never forward the configured API key to another host."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


OPENER = build_opener(_NoRedirect)


class MidjourneyError(RuntimeError):
    """An error safe to return to an AstrBot conversation."""


def _valid_https_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc
        and not parsed.username
        and not parsed.password
    )


class MidjourneyClient:
    """Submit one imagine job or query a prior task, without paid retries."""

    def __init__(self, api_key: str) -> None:
        token = api_key.strip()
        if (
            not token
            or token.lower().startswith("bearer ")
            or token.startswith("platform-")
        ):
            raise MidjourneyError(
                "Set an Ace Data Cloud generation API key in plugin settings."
            )
        self._api_key = token

    def _post(self, path: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
        request = Request(
            API_BASE + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AceDataCloudAstrBot/0.1.0",
            },
            method="POST",
        )
        try:
            with OPENER.open(request, timeout=90) as response:
                body = json.load(response)
                header_trace = response.headers.get(
                    "x-trace-id", ""
                ) or response.headers.get("x-request-id", "")
        except HTTPError as exc:
            raise MidjourneyError(
                f"Ace Data Cloud returned HTTP {exc.code}. Check service access and request history."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise MidjourneyError(
                "The API connection failed. Check request history before submitting another image."
            ) from None
        except (ValueError, UnicodeError):
            raise MidjourneyError(
                "The API returned invalid JSON. Check request history before retrying."
            ) from None
        if not isinstance(body, dict):
            raise MidjourneyError("The API returned an unexpected response format.")
        return body, str(body.get("trace_id") or header_trace)

    async def submit(
        self,
        prompt: str,
        version: str = "8.1",
        split_images: bool = False,
    ) -> dict[str, Any]:
        """Submit one fast, standard-definition 2×2 grid generation."""
        prompt = prompt.strip()
        if not prompt or len(prompt) > 4000:
            raise MidjourneyError("Provide an image prompt of 1–4000 characters.")
        if BILLING_FLAGS.search(prompt):
            raise MidjourneyError(
                "Set the model with the version argument; billing-impact prompt flags are not supported in this plugin."
            )
        if version not in VERSIONS:
            raise MidjourneyError(
                "Choose Midjourney version 8.1, 8, 7, 6.1, 6, or 5.2."
            )
        if not isinstance(split_images, bool):
            raise MidjourneyError("Split images must be true or false.")
        payload = {
            "action": "generate",
            "prompt": prompt,
            "mode": "fast",
            "version": version,
            "hd": False,
            "translation": False,
            "split_images": split_images,
            "async": True,
        }
        body, trace_id = await asyncio.to_thread(
            self._post, "/midjourney/imagine", payload
        )
        if body.get("success") is False or body.get("error"):
            raise MidjourneyError(
                "Image submission was rejected. Check request history before trying again."
            )
        task_id = body.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise MidjourneyError(
                "No task ID was returned. Check request history before submitting again."
            )
        return {
            "status": "submitted",
            "task_id": task_id,
            "trace_id": trace_id,
            "next_step": "Query this same task ID; do not submit another image while it is pending.",
        }

    async def query(self, task_id: str) -> dict[str, Any]:
        """Return grid and optional split-image URLs only after terminal success."""
        task_id = task_id.strip()
        if not task_id or len(task_id) > 128:
            raise MidjourneyError("Pass the exact task ID from Midjourney submission.")
        body, trace_id = await asyncio.to_thread(
            self._post,
            "/midjourney/tasks",
            {"id": task_id, "action": "retrieve"},
        )
        if body.get("success") is False or body.get("error"):
            raise MidjourneyError("Task lookup failed. Check request history.")
        response = body.get("response")
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                response = None
        if not isinstance(response, dict):
            response = {}
        trace_id = str(response.get("trace_id") or body.get("trace_id") or trace_id)
        state = str(body.get("state") or body.get("status") or "").lower()
        if state in FAILED or response.get("success") is False or response.get("error"):
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "failed",
                "success": False,
                "image_url": "",
                "sub_image_urls": [],
            }
        if not body.get("finished_at") or response.get("success") is not True:
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "pending",
                "success": False,
                "image_url": "",
                "sub_image_urls": [],
            }
        image_url = response.get("image_url")
        if not isinstance(image_url, str) or not _valid_https_url(image_url):
            image_url = ""
        sub_images = response.get("sub_image_urls")
        sub_image_urls = (
            [
                url
                for url in sub_images
                if isinstance(url, str) and _valid_https_url(url)
            ]
            if isinstance(sub_images, list)
            else []
        )
        cost = response.get("cost")
        public_cost = (
            {
                key: cost[key]
                for key in ("amount", "list_amount", "currency")
                if key in cost
            }
            if isinstance(cost, dict)
            else {}
        )
        return {
            "task_id": task_id,
            "trace_id": trace_id,
            "status": "succeeded" if image_url else "failed",
            "success": bool(image_url),
            "image_url": image_url,
            "sub_image_urls": sub_image_urls if image_url else [],
            "image_id": str(response.get("image_id") or "") if image_url else "",
            "image_width": response.get("image_width") if image_url else None,
            "image_height": response.get("image_height") if image_url else None,
            "cost": public_cost,
        }
