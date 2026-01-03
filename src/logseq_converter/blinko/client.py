import json
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional


class BlinkoClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._validate_token()

    def _validate_token(self):
        """
        Validates that the token looks like a JWT (3 parts separated by dots).
        """
        if not self.token:
            raise ValueError("Blinko token is empty")

        parts = self.token.split(".")
        if len(parts) != 3:
            raise ValueError("Provided token does not look like a valid JWT (must have 3 parts)")

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": "logseq-to-blinko-converter",
        }

    def upsert_note(self, content: str, original_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Upserts a note to Blinko.
        Currently mostly creates a new note as we don't have a reliable way to map Logseq IDs
        to Blinko integer IDs without state.
        If we had state, we would pass 'id' in the payload.
        """
        url = f"{self.base_url}/v1/note/upsert"

        payload = {
            "content": content,
            # 0 usually means "Memo" (Blinko), 1 means "Note".
            # User requested to save as "Notes".
            "type": 1,
            "isArchived": False,
            "isRecycle": False,
        }

        if original_id is not None:
            payload["id"] = original_id

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self._get_headers(), method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise RuntimeError(f"Blinko API returned status {response.status}")

                response_data = response.read()
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"Blinko API error: {e.code} - {error_body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Blinko: {e.reason}") from e

    def list_notes(self, page: int = 1, size: int = 100) -> List[Dict[str, Any]]:
        """
        Lists notes from Blinko.
        """
        url = f"{self.base_url}/v1/note/list"

        payload = {
            "page": page,
            "size": size,
            "isArchived": None,  # Retrieve both archived and active
            "isRecycle": False,  # Except recycled? Or maybe we should clear recycle bin too?
            # API spec says `isRecycle` default false.
            # If we want to delete absolutely everything, we should probably check recycle too?
            # But `batch-delete` might just move to recycle bin?
            # API has `/v1/note/batch-trash` and `/v1/note/batch-delete`.
            # Let's assume `batch-delete` is permanent or at least what we want.
            # "type": -1 # default -1 means all types
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self._get_headers(), method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise RuntimeError(f"Blinko API returned status {response.status}")

                response_data = response.read()
                return json.loads(response_data)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"Blinko API error: {e.code} - {error_body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Blinko: {e.reason}") from e

    def batch_delete(self, ids: List[int]) -> None:
        """
        Permanently deletes a batch of notes.
        """
        url = f"{self.base_url}/v1/note/batch-delete"

        payload = {"ids": ids}

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=self._get_headers(), method="POST")

        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise RuntimeError(f"Blinko API returned status {response.status}")
                # Response body is usually empty or success bool, read it anyway to consume
                response.read()
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"Blinko API error: {e.code} - {error_body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Failed to connect to Blinko: {e.reason}") from e

    def delete_all(self, dry_run: bool = False, progress_callback: Optional[Callable[[int, int], None]] = None) -> int:
        """
        Deletes ALL notes from Blinko.

        Args:
            dry_run: If True, only simulate deletion (fetch IDs and report).
            progress_callback: Optional callback(deleted_count, total_count).

        Returns:
            Total number of deleted notes.
        """
        # Step 1: Fetch all IDs
        all_ids: List[int] = []
        page = 1
        page_size = 100

        while True:
            notes = self.list_notes(page=page, size=page_size)
            if not notes:
                break

            ids = [note["id"] for note in notes]
            all_ids.extend(ids)

            if len(notes) < page_size:
                break

            page += 1

        total_count = len(all_ids)
        if total_count == 0:
            if progress_callback:
                progress_callback(0, 0)
            return 0

        # Step 2: Delete in batches
        batch_size = 50
        deleted_count = 0

        # Initial report
        if progress_callback:
            progress_callback(0, total_count)

        for i in range(0, total_count, batch_size):
            batch_ids = all_ids[i : i + batch_size]

            if not dry_run:
                self.batch_delete(batch_ids)

            deleted_count += len(batch_ids)

            if progress_callback:
                progress_callback(deleted_count, total_count)

        return total_count
