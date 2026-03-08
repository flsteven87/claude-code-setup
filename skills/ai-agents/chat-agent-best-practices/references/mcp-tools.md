## 5. MCP Tools Pattern

### Tool Registration with FastMCP

```python
from mcp.server.fastmcp import FastMCP, Context
from functools import lru_cache

mcp = FastMCP(name="my-agent")

@lru_cache
def get_service() -> MyService:
    """Singleton service - don't instantiate per call."""
    return MyService()

@mcp.tool()
async def my_tool(
    param: str,
    ctx: Context,
    user_id: str | None = None,
) -> dict:
    """Tool description for AI discovery.

    Args:
        param: Description of param
        ctx: MCP context (injected)
        user_id: User ID (for REST API transport)
    """
    effective_user_id = user_id or (ctx.client_id if ctx else None)
    if not effective_user_id:
        return {"error": "Authentication required", "success": False}

    service = get_service()
    try:
        result = await service.do_thing(param)
        ctx.info(f"Completed operation for {effective_user_id}")
        return {"success": True, "data": result}
    except ValidationError as e:
        return {"success": False, "error": str(e)}
```

### REST Wrapper with Typed Arguments

```python
from pydantic import BaseModel

# Avoid Any type - use explicit union
ToolArgumentValue = str | int | float | bool | list[str] | None

class ToolCallRequest(BaseModel):
    arguments: dict[str, ToolArgumentValue] = {}

@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolCallRequest):
    try:
        result = await mcp.call_tool(tool_name, request.arguments)
        return {"result": result}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (KeyError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid arguments: {e}") from e
```

---

