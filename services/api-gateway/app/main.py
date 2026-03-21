import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.openapi.utils import get_openapi

# Load environment variables
load_dotenv()

APP_NAME = os.getenv("APP_NAME", "API Gateway")
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# In docker-compose network, services can be reached by service name
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
BANKING_CORE_URL = os.getenv("BANKING_CORE_URL", "http://banking-core:8000")
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://voice-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL", "http://notification-service:8000"
)

app = FastAPI(title=APP_NAME)


@app.get("/health")
def health():
    return {"service": APP_NAME, "env": APP_ENV, "status": "UP"}


# ---- OpenAPI aggregation (so gateway Swagger shows all APIs) ----

def _rewrite_refs(obj: Any, mapping: Dict[str, str]) -> Any:
    """Recursively rewrite schema $ref strings based on mapping."""
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                for src, dst in mapping.items():
                    if v == f"#/components/schemas/{src}":
                        v = f"#/components/schemas/{dst}"
                        break
                out[k] = v
            else:
                out[k] = _rewrite_refs(v, mapping)
        return out
    if isinstance(obj, list):
        return [_rewrite_refs(x, mapping) for x in obj]
    return obj


def _merge_openapi(
    base: Dict[str, Any],
    incoming: Dict[str, Any],
    *,
    path_prefix: str = "",
    schema_prefix: str = "",
) -> None:
    base.setdefault("paths", {})
    base.setdefault("components", {})
    base["components"].setdefault("schemas", {})

    incoming_paths = incoming.get("paths") or {}
    incoming_schemas = ((incoming.get("components") or {}).get("schemas")) or {}

    # Prefix schemas (and rewrite refs) to avoid cross-service collisions
    schema_name_map = {
        name: f"{schema_prefix}{name}" if schema_prefix else name
        for name in incoming_schemas.keys()
    }

    rewritten_paths = _rewrite_refs(incoming_paths, schema_name_map)
    rewritten_schemas = _rewrite_refs(incoming_schemas, schema_name_map)

    for p, item in rewritten_paths.items():
        base["paths"][f"{path_prefix}{p}"] = item

    for name, schema in rewritten_schemas.items():
        out_name = f"{schema_prefix}{name}" if schema_prefix else name
        base["components"]["schemas"][out_name] = schema


def custom_openapi() -> Dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    # Start from gateway-native endpoints (e.g., /health)
    base = get_openapi(title=APP_NAME, version="1.0.0", routes=app.routes)

    services = (
        # (service_base_url, path_prefix_in_gateway, schema_prefix)
        (USER_SERVICE_URL, "/user", "User__"),
        (BANKING_CORE_URL, "/bank", "Banking__"),
        # gateway-only prefix: child voice-service routes live under /api/v1/...
        (VOICE_SERVICE_URL, "/voice", "Voice__"),
        (NOTIFICATION_SERVICE_URL, "/notification", "Notif__"),
    )

    for base_url, path_prefix, schema_prefix in services:
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(f"{base_url}/openapi.json")
                r.raise_for_status()
                spec = r.json()
            _merge_openapi(
                base,
                spec,
                path_prefix=path_prefix,
                schema_prefix=schema_prefix,
            )
        except Exception:
            # Don't fail gateway docs if one service is down
            continue

    app.openapi_schema = base
    return app.openapi_schema


app.openapi = custom_openapi


# ---- Reverse proxy routing ----

def _route_for_path(path: str) -> Optional[tuple[str, str]]:
    """Map gateway path -> (upstream_base_url, upstream_path)."""

    # user-service
    if path.startswith("/user"):
        # /user -> /health, /user/anything -> /anything
        rest = path[len("/user") :]  # includes leading '/' or is empty
        if rest in ("", "/", "/health"):
            return USER_SERVICE_URL, "/health"
        return USER_SERVICE_URL, rest

    # banking-core
    if path.startswith("/bank"):
        # /bank -> /health, /bank/accounts -> /accounts
        rest = path[len("/bank") :]
        if rest in ("", "/", "/health"):
            return BANKING_CORE_URL, "/health"
        return BANKING_CORE_URL, rest

    # voice-service
    if path.startswith("/voice"):
        # /voice -> /health, /voice/health -> /health, /voice/api/v1/... -> /api/v1/...
        rest = path[len("/voice") :]
        if rest in ("", "/", "/health"):
            return VOICE_SERVICE_URL, "/health"
        return VOICE_SERVICE_URL, rest

    # notification-service
    if path.startswith("/notification"):
        rest = path[len("/notification") :]
        if rest in ("", "/", "/health"):
            return NOTIFICATION_SERVICE_URL, "/health"
        return NOTIFICATION_SERVICE_URL, rest

    return None


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
}


def _filter_headers(headers: Dict[str, str]) -> Dict[str, str]:
    return {k: v for k, v in headers.items() if k.lower() not in HOP_BY_HOP_HEADERS}


@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    include_in_schema=False,
)
async def proxy(full_path: str, request: Request) -> Response:
    path = "/" + full_path

    # keep gateway-native endpoints
    if path in {"/health", "/docs", "/redoc", "/openapi.json"}:
        raise HTTPException(status_code=404, detail="Not a proxied route")

    routed = _route_for_path(path)
    if not routed:
        raise HTTPException(status_code=404, detail="No route configured for this path")

    upstream_base, upstream_path = routed
    target_url = upstream_base.rstrip("/") + upstream_path

    body = await request.body()
    headers = _filter_headers(dict(request.headers))

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.request(
                request.method,
                target_url,
                content=body if body else None,
                headers=headers,
                params=request.query_params,
            )

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=_filter_headers(dict(resp.headers)),
            media_type=resp.headers.get("content-type"),
        )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Upstream service unavailable")


if __name__ == "__main__":
    import uvicorn

    # Avoid reload/import-string issues inside containers
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT, reload=False)
