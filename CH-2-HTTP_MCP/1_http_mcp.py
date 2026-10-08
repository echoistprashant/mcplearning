from fastmcp import FastMCP


mcp = FastMCP()

@mcp.tool
async def fetch():
    '''Use this tool to fetch the data from the source'''
    #Simulate fetching data from a source
    '''You can make some api call here to fetch data from a database'''

    return {"data":"hello, mcp!"}

@mcp.tool
async def process(path:str):
    '''Use this tool to process the fetched data '''
    '''You can perform some data transformation here'''

    return {"processed data" : "data has been proccessed! at path:" + path}


if __name__ == "__main__":
    mcp.run(transport="streamable-http",host="0.0.0.0",port=8050)