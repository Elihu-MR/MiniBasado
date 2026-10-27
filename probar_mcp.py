import asyncio
from pathlib import Path
from fastmcp import Client
 
async def main():
    async with Client(Path("mcp_server/server.py")) as c:
        print([t.name for t in await c.list_tools()])
 
asyncio.run(main())
