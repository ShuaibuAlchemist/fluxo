# Backend data layer & Agent API (reference)

This is a concise, developer-focused reference that documents the backend data layer, agent interface APIs, and recommended file locations in the Fluxo repo. Use this when implementing agents, services, tasks, or pipeline adapters.

## Quick reference (paths)

- Services (live fetchers): `fluxo/backend/services/` (e.g. , `thegraph.py`, )
- Data pipeline artifacts (canonical/denormalized): `fluxo/backend/data_pipeline/` (/DB/function outputs)
- Agents: `fluxo/backend/agents/` (e.g. `onchain_agent.py`)
- Celery tasks: `fluxo/backend/tasks/agent_tasks/`
- API models: `fluxo/backend/api/models/`
- API routes: `fluxo/backend/api/routes/`
- Docs: `fluxo/backend/docs/`

## Agent interface API (Access Agents data through these endpoints)
- onchain_agent : `agent/onchain/`, `agent/protocols` 
- risk agent : `agent/audit-check`, `agent/audits/{protocol}`, `agent/risk`
- social agent : `agent/sentiment` , `agent/narratives/{token_symbol}`, `agent/platforms/{token_symbol}` , `agent/supported-pltaform`, `agent/social`

check out  `fluxo/backend/api/routes` for API route endpoint


## Design principles

- Pipeline outputs are the canonical source for aggregated/historical datasets. When available and up-to-date, agents should prefer pipeline artifacts for deterministic and fast analysis.
- Services under `services/` provide live data when pipeline artifacts are missing or freshness is required.
- Keep services side-effect free: accept inputs, return normalized dicts (or typed dataclasses), and raise typed exceptions for recoverable/unrecoverable errors.
- Agents orchestrate services/pipeline adapters, compute signals/alerts, and return JSON-serializable payloads. Agents should not perform persistence (Celery tasks do that).

## Agent contract (recommended minimal API)

Create agents as small classes under `fluxo/backend/agents/` with a stable interface. Example:

```py
# fluxo/backend/agents/onchain_agent.py
from typing import Dict

class AgentBase:
    async def analyze_wallet(self, wallet: str, *, network: str = 'mantle') -> Dict:
        """Return a JSON-serializable summary for a wallet."""

    async def analyze_protocol(self, protocol_slug: str) -> Dict:
        """Return analysis for a protocol (TVL, flows, risks)."""

# Example concrete usage inside a Celery task (sync wrapper):
# loop = asyncio.new_event_loop(); result = loop.run_until_complete(agent.analyze_wallet(wallet))
```

Expected result shape (example):

{
  "wallet": "0x...",
  "network": "mantle",
  "timestamp": "2025-11-18T12:00:00Z",
  "total_value_usd": 12345.67,
  "assets": [
    {"token_address":"0x..","symbol":"MNT","balance":1000,"value_usd":5000,"percentage":40.5},
  ],
  "alerts": [ ... ],
  "meta": {"source":"pipeline|dune|rpc"}
}

Error modes
- Services raise typed errors (ServiceError, ProviderTimeout, NotFound).
- Agents should raise AgentError or return failure payloads if they cannot produce analysis.
- Celery tasks must catch exceptions and call `self.update_state(state='FAILURE', meta={'error': str(e)})` and return a failure object.



## Pydantic models (suggested file)

Place models under `fluxo/backend/api/models/` and reuse them in API routes and Celery tasks. Example file scaffold to add:

`fluxo/backend/api/models/portfolio.py`

```py
from pydantic import BaseModel
from typing import List

class Asset(BaseModel):
    token_address: str
    token_symbol: str
    balance: float
    value_usd: float
    percentage: float

class PortfolioAnalysis(BaseModel):
    wallet: str
    network: str
    total_value_usd: float
    assets: List[Asset]
    timestamp: str
```

Using the models
- Use these models to validate agent outputs before persisting or returning them via API.
- Convert Decimal → float only when constructing the Pydantic model to avoid serialization surprises.

## Celery tasks & API wiring

Pattern:
- POST /agent/onchain/analyze -> enqueue Celery task `onchain.analyze.delay(wallet, network)` and return `task_id`.
- Worker task calls agent, validates output via Pydantic models, persists result in Redis/DB, and returns result.
- GET /agent/onchain/status/{task_id} -> query Celery AsyncResult and if finished return stored result or Celery result.

Runbook example (repo root):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
celery -A core.celery_app worker --loglevel=info
```
