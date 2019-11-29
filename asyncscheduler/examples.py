from . import Scheduler
import asyncio
import pytz

timezone = pytz.timezone('US/Eastern')
jobs = Scheduler(timezone)

@jobs.schedule(at="04:00PM", on="Friday,Thursday,Wednesday,Tuesday,Monday")
async def test_job():
    print("The Stock Market is Closing!")
    await asyncio.sleep(0)
    
@jobs.schedule(minutes=1, on="Friday")
async def test_job():
    print("fizz on fridays")
    await asyncio.sleep(0)

@jobs.schedule(seconds=1, on="Monday")
async def test_job2():
    print("fizz on mondays")
    await asyncio.sleep(0)
    
@jobs.schedule(minutes=5)
async def test_job3():
    print("buzz")
    await asyncio.sleep(0)
    
jobs.start()