"""ClaudeNasConnector — MCP server.

A self-hosted MCP server you add to the Claude apps as a custom connector.

Authentication is optional and turns on automatically when the OIDC_* environment
variables are set: the server then acts as an OAuth 2.1 resource server via
FastMCP's OIDC proxy, using your own identity provider (e.g. Pocket ID, Authentik,
Keycloak, Auth0) as the login backend. Without those variables it runs OPEN
(fine for local testing — never expose an unauthenticated server publicly).
"""
import os

from fastmcp import FastMCP

MEMORY_DIR = os.environ.get("MEMORY_DIR", "/data/memory")
SKILLS_DIR = os.environ.get("SKILLS_DIR", "/data/skills")
HOST = os.environ.get("MCP_HOST", "0.0.0.0")
PORT = int(os.environ.get("MCP_PORT", "8787"))


def _build_auth():
    """Enable OAuth (OIDC proxy) when OIDC_CONFIG_URL + OIDC_CLIENT_ID are set."""
    config_url = os.environ.get("OIDC_CONFIG_URL")
    client_id = os.environ.get("OIDC_CLIENT_ID")
    if not (config_url and client_id):
        return None

    from fastmcp.server.auth.oidc_proxy import OIDCProxy

    return OIDCProxy(
        config_url=config_url,
        client_id=client_id,
        client_secret=os.environ.get("OIDC_CLIENT_SECRET"),
        base_url=os.environ.get("BASE_URL", f"http://localhost:{PORT}"),
        required_scopes=["openid", "profile", "email"],
        jwt_signing_key=os.environ.get("JWT_SIGNING_KEY"),
    )


auth = _build_auth()
mcp = FastMCP("ClaudeNasConnector", auth=auth)


@mcp.tool
def ping(name: str = "world") -> str:
    """Health check — confirms the connector is reachable."""
    return f"Hello {name}, your NAS MCP server is alive! 🎉"


# --- Roadmap: memory_read / memory_write / memory_list ---
# --- Roadmap: skill_search / skill_load / skill_resource ---


if __name__ == "__main__":
    print(f"[ClaudeNasConnector] auth: {'OIDC proxy' if auth else 'OPEN (no auth)'}")
    # Streamable-HTTP transport — what Claude custom connectors speak.
    # Endpoint: http://HOST:PORT/mcp
    mcp.run(transport="http", host=HOST, port=PORT)
