"""Minimal Flipside Crypto API client prototype.

This implements a small helper to submit SQL queries and poll for results.
See: https://developer.flipsidecrypto.com/ for production details.

Note: This is a prototype with simple polling and no advanced retry/backoff.
"""
from __future__ import annotations
import os
import time
import requests
from typing import Dict, Any, Optional

FLIPSIDE_API_KEY = os.getenv("FLIPSIDE_API_KEY")
FLIPSIDE_API_URL = os.getenv("FLIPSIDE_API_URL", "https://api.flipsidecrypto.com")

class FlipsideError(Exception):
    pass


def submit_query(sql: str, ttl_minutes: int = 10, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Submit a SQL query to Flipside and return the query metadata (including query_id).
    Raises FlipsideError on failure.
    """
    key = api_key or FLIPSIDE_API_KEY
    if not key:
        raise FlipsideError("FLIPSIDE_API_KEY is not set")

    url = f"{FLIPSIDE_API_URL}/api/v2/queries"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {"sql": sql, "ttlMinutes": ttl_minutes}
    resp = requests.post(url, json=body, headers=headers, timeout=30)
    try:
        resp.raise_for_status()
    except Exception as e:
        raise FlipsideError(f"submit_query failed: {e} - {resp.text}")
    return resp.json()


def fetch_query_result(query_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Poll the flipside query result endpoint until complete or until timeout.
    Returns the final result JSON (may contain `results` key with rows).
    """
    key = api_key or FLIPSIDE_API_KEY
    if not key:
        raise FlipsideError("FLIPSIDE_API_KEY is not set")

    status_url = f"{FLIPSIDE_API_URL}/api/v2/queries/{query_id}"
    result_url = f"{FLIPSIDE_API_URL}/api/v2/queries/{query_id}/results"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    # small polling loop
    timeout_seconds = 60
    start = time.time()
    while True:
        resp = requests.get(status_url, headers=headers, timeout=15)
        try:
            resp.raise_for_status()
        except Exception as e:
            raise FlipsideError(f"fetch status failed: {e} - {resp.text}")
        status = resp.json().get("status")
        if status == "finished":
            # fetch results
            r = requests.get(result_url, headers=headers, timeout=30)
            try:
                r.raise_for_status()
            except Exception as e:
                raise FlipsideError(f"fetch result failed: {e} - {r.text}")
            return r.json()
        if status == "failed":
            raise FlipsideError(f"Query {query_id} failed: {resp.json()}")
        if time.time() - start > timeout_seconds:
            raise FlipsideError("Timeout waiting for Flipside query result")
        time.sleep(1)


def run_sql_and_get_results(sql: str, ttl_minutes: int = 10, api_key: Optional[str] = None) -> Dict[str, Any]:
    meta = submit_query(sql, ttl_minutes=ttl_minutes, api_key=api_key)
    query_id = meta.get("queryId") or meta.get("id") or meta.get("query_id")
    if not query_id:
        # Try common keys, otherwise return meta
        raise FlipsideError(f"Could not extract query_id from response: {meta}")
    return fetch_query_result(query_id, api_key=api_key)


if __name__ == "__main__":
    sample_sql = "SELECT 1 as col;"
    try:
        print('Submitting sample SQL to Flipside...')
        res = run_sql_and_get_results(sample_sql)
        print('Result:', res)
    except Exception as e:
        print('Flipside demo failed:', e)
