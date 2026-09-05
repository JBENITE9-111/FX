from __future__ import annotations

import asyncio
import time
import traceback
import uuid
from typing import Any, Awaitable, Callable


class BackgroundJobManager:

    def __init__(self):

        self.jobs: dict[
            str,
            dict[str, Any]
        ] = {}

    def _new(
        self,
        job_type: str,
    ):

        job_id = str(
            uuid.uuid4()
        )

        self.jobs[
            job_id
        ] = {
            "id": job_id,
            "type": job_type,
            "status": "RUNNING",
            "created_at": time.time(),
            "updated_at": time.time(),
            "result": None,
            "error": None,
        }

        return job_id

    def get(
        self,
        job_id: str,
    ):

        return self.jobs.get(
            job_id
        )

    def all_jobs(self):

        return list(
            self.jobs.values()
        )[-100:]

    def submit_async(
        self,
        job_type: str,
        worker: Callable[
            [],
            Awaitable[Any],
        ],
    ):

        job_id = self._new(
            job_type
        )

        async def runner():

            try:

                result = await worker()

                self.jobs[
                    job_id
                ][
                    "status"
                ] = "COMPLETE"

                self.jobs[
                    job_id
                ][
                    "result"
                ] = result

            except Exception as exc:

                self.jobs[
                    job_id
                ][
                    "status"
                ] = "FAILED"

                self.jobs[
                    job_id
                ][
                    "error"
                ] = str(exc)

                self.jobs[
                    job_id
                ][
                    "trace"
                ] = (
                    traceback
                    .format_exc()
                )

            self.jobs[
                job_id
            ][
                "updated_at"
            ] = time.time()

        asyncio.create_task(
            runner()
        )

        return job_id

    def submit_sync(
        self,
        job_type: str,
        worker: Callable[
            [],
            Any,
        ],
    ):

        async def wrapper():

            return await asyncio.to_thread(
                worker
            )

        return self.submit_async(
            job_type,
            wrapper,
        )


jobs = BackgroundJobManager()
