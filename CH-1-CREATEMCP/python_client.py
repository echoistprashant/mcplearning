import os 
import sys
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import asyncio


#path to the mcp server 

mcp_server_script = os.path.join((os.path.dirname(os.path.abspath(__file__))),"creatingmcp.py")
print(mcp_server_script)

#creating the server parameter

server_params = StdioServerParameters(
    command=sys.executable,
    args=[str(mcp_server_script)],
)

#creating a client session 

async def main():
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            #fetch the tools
            tools = await session.list_tools()
            print("available tools:", tools)

            #use the fetch tool

            result = await session.call_tool("process",arguments={"path": "/path/to/data"})
            print("Result", result)


if __name__ == "__main__":
    asyncio.run(main())            
