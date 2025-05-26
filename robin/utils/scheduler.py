import asyncio
import datetime
from typing import Dict, List, Optional, Callable, Any
import pytz
from discord.ext import tasks

class Scheduler:
    def __init__(self, bot):
        self.bot = bot
        self.tasks: Dict[str, tasks.Loop] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.timezone = pytz.UTC  # Default to UTC
    
    def set_timezone(self, timezone: str):
        """Set the timezone for scheduled tasks"""
        try:
            self.timezone = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone: {timezone}")
    
    def add_task(self, name: str, callback: Callable, interval: int, 
                 start_time: Optional[datetime.time] = None):
        """Add a new scheduled task
        
        Args:
            name: Unique identifier for the task
            callback: Async function to call
            interval: Interval in seconds between executions
            start_time: Optional time of day to start the task
        """
        if name in self.tasks:
            raise ValueError(f"Task {name} already exists")
        
        @tasks.loop(seconds=interval)
        async def task_loop():
            if start_time:
                now = datetime.datetime.now(self.timezone).time()
                if now < start_time:
                    return
            
            try:
                await callback()
            except Exception as e:
                print(f"Error in scheduled task {name}: {str(e)}")
        
        self.tasks[name] = task_loop
        self.callbacks[name] = [callback]
        task_loop.start()
    
    def remove_task(self, name: str):
        """Remove a scheduled task"""
        if name in self.tasks:
            self.tasks[name].cancel()
            del self.tasks[name]
            del self.callbacks[name]
    
    def add_callback(self, task_name: str, callback: Callable):
        """Add a callback to an existing task"""
        if task_name not in self.callbacks:
            raise ValueError(f"Task {task_name} does not exist")
        self.callbacks[task_name].append(callback)
    
    def remove_callback(self, task_name: str, callback: Callable):
        """Remove a callback from a task"""
        if task_name in self.callbacks and callback in self.callbacks[task_name]:
            self.callbacks[task_name].remove(callback)
    
    def get_task_info(self, name: str) -> Dict[str, Any]:
        """Get information about a scheduled task"""
        if name not in self.tasks:
            raise ValueError(f"Task {name} does not exist")
        
        task = self.tasks[name]
        return {
            'name': name,
            'interval': task.seconds,
            'is_running': task.is_running(),
            'next_iteration': task.next_iteration,
            'callbacks': len(self.callbacks[name])
        }
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get information about all scheduled tasks"""
        return [self.get_task_info(name) for name in self.tasks.keys()]
    
    async def run_task_now(self, name: str):
        """Run a scheduled task immediately"""
        if name not in self.tasks:
            raise ValueError(f"Task {name} does not exist")
        
        for callback in self.callbacks[name]:
            try:
                await callback()
            except Exception as e:
                print(f"Error running task {name}: {str(e)}")
    
    def stop_all(self):
        """Stop all scheduled tasks"""
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()
        self.callbacks.clear() 