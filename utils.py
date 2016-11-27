from asyncio import iscoroutinefunction


async def call_maybe_async(func, *args, **kwargs):
    if iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)
