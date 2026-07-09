def block_type(block):
    if isinstance(block, dict):
        return block.get("type", "text")
    return getattr(block, "type", "text")


def extract_text(content) -> str | None:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for block in content:
            if block_type(block) == "text":
                return block.get("text", "") or getattr(block, "text", "")
    return None


def has_tool_use(content) -> bool:
    if not isinstance(content, list):
        return False
    return any(block_type(b) == "tool_use" for b in content)


def call_tool_handler(handler, params, name: str):
    if handler is None:
        return f"Handler not found for {name}"
    if isinstance(params, dict):
        try:
            return handler(**params)
        except TypeError:
            return handler(params)
    return handler(params)
