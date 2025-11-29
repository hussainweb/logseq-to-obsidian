import os
import sys
import time
from typing import List, Optional

import requests

from logseq_converter.tana.models import TanaAPIPayload, TanaNode


class TanaClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TANA_API_KEY")
        if not self.api_key:
            raise ValueError("TANA_API_KEY environment variable is not set.")
        self.base_url = "https://europe-west1-tagr-prod.cloudfunctions.net/addToNodeV2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def send_nodes(self, nodes: List[TanaNode], target_node_id: str = "INBOX"):
        """
        Sends nodes to Tana API in batches of 100.
        Respects the 1 request per second rate limit.
        """
        batch_size = 100
        total_batches = (len(nodes) + batch_size - 1) // batch_size

        print(f"Sending {len(nodes)} nodes in {total_batches} batch(es)...", file=sys.stderr)

        for i in range(0, len(nodes), batch_size):
            batch_num = (i // batch_size) + 1
            batch = nodes[i : i + batch_size]
            payload = TanaAPIPayload(targetNodeId=target_node_id, nodes=batch)

            print(f"Sending batch {batch_num}/{total_batches} ({len(batch)} nodes)...", file=sys.stderr)

            try:
                self._send_batch(payload)
                print(f"Batch {batch_num}/{total_batches} sent successfully.", file=sys.stderr)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print("Rate limit exceeded. Please wait and try again later.", file=sys.stderr)
                    raise
                elif e.response.status_code in (401, 403):
                    print("Authentication failed. Please check your TANA_API_KEY.", file=sys.stderr)
                    raise
                else:
                    print(f"HTTP error occurred: {e}", file=sys.stderr)
                    raise
            except requests.exceptions.RequestException as e:
                print(f"Network error occurred: {e}", file=sys.stderr)
                raise

            # Simple throttling: sleep 1 second after each request except the last
            if i + batch_size < len(nodes):
                time.sleep(1)

    def _send_batch(self, payload: TanaAPIPayload):
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload.model_dump(exclude_none=True),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
