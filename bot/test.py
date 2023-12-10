import asyncio

async def test():
    await asyncio.sleep(3)

# Create an event loop
loop = asyncio.get_event_loop()

# Run the test function asynchronously
loop.run_until_complete(test())

print("test")
