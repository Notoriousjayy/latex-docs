"""Illustrative local stdio server; MCP SDK required, not tested live."""
from mcp.server.fastmcp import FastMCP
server = FastMCP('engineering-policy')

@server.tool()
def policy_summary(policy_id: str) -> str:
    """Return an allowlisted synthetic engineering policy."""
    if policy_id != 'pricing-validation':
        raise ValueError('unknown policy')
    return 'Edit only pricing.py; independent tests and human review required.'

if __name__ == '__main__':
    server.run(transport='stdio')
