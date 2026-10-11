"""Midjourney image tools for AstrBot through Ace Data Cloud."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import MidjourneyClient, MidjourneyError


class MidjourneyPlugin(Star):
    """Expose one imagine submission and one existing-task lookup tool."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="midjourney_imagine")
    async def midjourney_imagine(
        self,
        event: AstrMessageEvent,
        prompt: str,
        version: str = "8.1",
        split_images: bool = False,
    ) -> str:
        """Submit one billable Midjourney image grid job.

        Args:
            prompt(string): Description of the desired image grid.
            version(string): Midjourney version 8.1, 8, 7, 6.1, 6, or 5.2.
            split_images(boolean): Return four separate images with the grid.

        Returns:
            JSON submission status and task ID, never a finished-image claim.
        """
        try:
            result = await MidjourneyClient(self.config.get("api_key", "")).submit(
                prompt, version, split_images
            )
        except MidjourneyError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="midjourney_get_task")
    async def midjourney_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query a prior Midjourney task without another generation.

        Args:
            task_id(string): Exact task ID from midjourney_imagine.

        Returns:
            JSON status and final grid image URL only after task completion.
        """
        try:
            result = await MidjourneyClient(self.config.get("api_key", "")).query(
                task_id
            )
        except MidjourneyError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)
