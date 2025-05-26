#!/usr/bin/env python3
"""
Database module for handling user preferences
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class PreferencesDB:
    def __init__(self, db_path=None):
        """Initialize the preferences database"""
        if db_path is None:
            # Default to a preferences.json in the same directory
            self.db_path = Path(os.path.dirname(os.path.abspath(__file__))) / "preferences.json"
        else:
            self.db_path = Path(db_path)
            
        # Create the directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize the database if it doesn't exist
        if not self.db_path.exists():
            with open(self.db_path, 'w') as f:
                json.dump({}, f)
            logger.info(f"Created new preferences database at {self.db_path}")
        
        logger.info(f"Using preferences database at {self.db_path}")
    
    def get_user_preferences(self, user_id):
        """Get preferences for a user"""
        try:
            with open(self.db_path, 'r') as f:
                all_prefs = json.load(f)
            
            # Convert user_id to string for JSON compatibility
            user_id = str(user_id)
            
            # Return existing preferences or empty dict for new users
            return all_prefs.get(user_id, {})
        except Exception as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {e}")
            return {}
    
    def set_user_preferences(self, user_id, preferences):
        """Set preferences for a user"""
        try:
            # Read existing preferences
            with open(self.db_path, 'r') as f:
                all_prefs = json.load(f)
            
            # Convert user_id to string for JSON compatibility
            user_id = str(user_id)
            
            # Update preferences
            all_prefs[user_id] = preferences
            
            # Write back to file
            with open(self.db_path, 'w') as f:
                json.dump(all_prefs, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error setting preferences for user {user_id}: {e}")
            return False
    
    def toggle_daily_brief(self, user_id, status):
        """Toggle daily brief status for a user"""
        try:
            # Get current preferences
            preferences = self.get_user_preferences(user_id)
            
            # Update brief_enabled status
            preferences['brief_enabled'] = status
            
            # Save updated preferences
            return self.set_user_preferences(user_id, preferences)
        except Exception as e:
            logger.error(f"Error toggling daily brief for user {user_id}: {e}")
            return False

