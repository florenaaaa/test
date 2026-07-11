from fastmcp import FastMCP

# 创建 Server 实例
server = FastMCP("my-mcp-server")

# 定义 Tool
@server.tool()
async def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    # 实际业务逻辑
    return f"{city} 今天晴天，温度 25°C"

# 定义 Resource
@server.resource("weather://forecast")
async def weather_forecast() -> str:
    """返回未来一周天气预报"""
    return "未来七天天气预报..."

# 启动 Server
if __name__ == "__main__":
    server.run(transport="http")