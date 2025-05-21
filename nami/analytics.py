import json
import logging
from datetime import datetime
from typing import Dict, Any
import asyncio

class Analytics:
    def __init__(self, analytics_file: str = "analytics.json"):
        self.analytics_file = analytics_file
        self.data = self._load_data()
        self._setup_logging()

    def _setup_logging(self):
        """Set up analytics logging"""
        self.logger = logging.getLogger("nami_analytics")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(filename="analytics.log", encoding='utf-8', mode='a')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(handler)

    def _load_data(self) -> Dict:
        """Load analytics data from file"""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'commands': {},
                'errors': {},
                'usage': {},
                'preferences': {}
            }

    def _save_data(self):
        """Save analytics data to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save analytics data: {e}")

    def log_command(self, command: str, user_id: int):
        """Log command usage"""
        if command not in self.data['commands']:
            self.data['commands'][command] = {}
        
        if user_id not in self.data['commands'][command]:
            self.data['commands'][command][user_id] = 0
        
        self.data['commands'][command][user_id] += 1
        self._save_data()
        self.logger.info(f"Command {command} used by user {user_id}")

    def log_error(self, command: str, error: str, user_id: int):
        """Log command errors"""
        if command not in self.data['errors']:
            self.data['errors'][command] = {}
        
        if error not in self.data['errors'][command]:
            self.data['errors'][command][error] = 0
        
        self.data['errors'][command][error] += 1
        self._save_data()
        self.logger.error(f"Error in {command} by user {user_id}: {error}")

    def log_preference(self, user_id: int, preference: str, value: Any):
        """Log user preferences"""
        if user_id not in self.data['preferences']:
            self.data['preferences'][user_id] = {}
        
        self.data['preferences'][user_id][preference] = value
        self._save_data()
        self.logger.info(f"User {user_id} set preference {preference} to {value}")

    async def generate_report(self):
        """Generate analytics report"""
        report = {
            'total_commands': sum(len(cmds) for cmds in self.data['commands'].values()),
            'total_errors': sum(len(errs) for errs in self.data['errors'].values()),
            'top_commands': self._get_top_commands(),
            'error_rates': self._get_error_rates(),
            'user_count': len(self.data['preferences'])
        }
        
        return report

    def _get_top_commands(self, limit: int = 5) -> Dict:
        """Get top used commands"""
        command_counts = {}
        for cmd, users in self.data['commands'].items():
            command_counts[cmd] = sum(users.values())
        
        return dict(sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:limit])

    def _get_error_rates(self) -> Dict:
        """Calculate error rates per command"""
        error_rates = {}
        for cmd, errors in self.data['errors'].items():
            total_errors = sum(errors.values())
            if cmd in self.data['commands']:
                total_uses = sum(self.data['commands'][cmd].values())
                error_rate = (total_errors / total_uses) * 100 if total_uses > 0 else 0
                error_rates[cmd] = f"{error_rate:.2f}%"
        
        return error_rates

# Initialize analytics
analytics = Analytics()
