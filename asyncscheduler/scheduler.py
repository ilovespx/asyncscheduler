import asyncio
import datetime as dt

#TODO:
#Write test and documentation
#PyPi
#Write examples for inheritance.
#Startup Events?
#Before Exit Events?

class Scheduler:
    def __init__(self,timezone):
        self._events = []
        self.timezone = timezone
        self._start_date = dt.datetime.now().replace(tzinfo=timezone)
        self._start_str = self._start_date.strftime("%d-%m-%y")

    def start(self):
        print("Started Scheduler.")
        if not self._events:
            print("No events to run. Proccess will exit.")
        else:
            self._run_event_loop()
        
    def _run_event_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        coroutines = [event.execute() for event in self._events]
        loop.run_until_complete(asyncio.gather(*coroutines))
        
    def schedule(self,*args,**kwargs):
        def _schedule(func):
            if not asyncio.iscoroutinefunction(func):
                raise RuntimeError(f"Event must be a coroutine, Scheduler received {type(func)}")
            event = ScheduledEvent(func,self.timezone,self._start_date,self._start_str,**kwargs)
            self._events.append(event)
            return func
        return _schedule

class ScheduledEvent:
    def __init__(self,event,timezone,start_date,start_date_str,**kwargs):
        self._event = event
        self.wait_interval = 0
        self._adjused_time = 0
        self.week_days = set()

        week_days = kwargs.get("on")
        if week_days:
            if isinstance(week_days,str):
                week_days = week_days.split(",")
            if isinstance(week_days,list):
                for day in week_days:
                    if isinstance(day,int): 
                        self._try_add_weekday(day)
                    elif isinstance(day,str):
                        self._try_add_weekday(self._convert_weekday(day))
            else:
                raise RuntimeError(f"On arguement requires string or list of weekdays, received {type(week_days)}")
            
        schedule_time = kwargs.get("at")
        if schedule_time:
            if isinstance(schedule_time,str):
                try:
                    schedule_time = self._parse_time(schedule_time,timezone,start_date,start_date_str)
                except:
                    raise RuntimeError(f"at arguement must be passed as Padded Hour:Minute:AM/PM or 24 Hour:Minute string")
            else:
                raise RuntimeError(f"at arguement requires string, received {type(schedule_time)}")

            self.wait_interval = (schedule_time-dt.datetime.now(timezone)).seconds
            self._adjused_time = int(24)*3600

        else:        
            seconds = kwargs.get("seconds")
            if seconds:
                self.wait_interval += int(seconds)
            
            minutes = kwargs.get("minutes")
            if minutes:
                self.wait_interval += int(minutes)*60
            
            hours = kwargs.get("hours")
            if hours:
                self.wait_interval += int(hours)*3600

    async def execute(self):
        while True:
            await self.wait()
            if self.can_execute: await self._event()

    @property
    def can_execute(self):
        if not self.week_days: return True
        return dt.datetime.today().weekday() in self.week_days

    async def wait(self):
        await asyncio.sleep(self.wait_interval)
        if self._adjused_time:
            self.wait_interval = self._adjused_time
            self._adjused_time = 0

    def _try_add_weekday(self,week_day):
        if week_day > -1 and week_day < 7:
            self.week_days.add(week_day)
            return True
        return False

    def _parse_time(self,schedule_time,timezone,start_date,start_date_str):
        schedule_time = f"{start_date_str} {schedule_time}"
        try:
            date = dt.datetime.strptime(schedule_time,"%d-%m-%y %I:%M%p")
        except:
            date =  dt.datetime.strptime(schedule_time,"%d-%m-%y %H:%M")
        date = date.replace(tzinfo=timezone)
        if date < start_date:
            date += dt.timedelta(days=1)
        return date

    def _convert_weekday(self,weekday):
        weekday = weekday.lower()
        if weekday == "monday": return 0
        if weekday == "tuesday": return 1
        if weekday == "wednesday": return 2
        if weekday == "thursday": return 3
        if weekday == "friday": return 4
        if weekday == "saturday": return 5
        if weekday == "sunday": return 6
        return -1


        
