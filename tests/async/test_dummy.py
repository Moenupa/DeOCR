import asyncio

import pytest


async def simple_async_function():
    await asyncio.sleep(0.01)
    return True


@pytest.mark.asyncio
async def test_simple_async_function():
    result = await simple_async_function()
    assert result, "Dummy async test didnt work, try running `pytest tests/async/`"
