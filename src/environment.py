import os
import sys
import logging

from dotenv import load_dotenv

# load dot env file
load_dotenv()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Environment(metaclass=Singleton):
    def _validate(self, key):
        env_var = os.getenv(key)

        if not env_var:
            logging.error(f'Missing required environment variable "{key}".')
            sys.exit(1)

        return env_var

    def _validate_optional(self, key, default=None):
        env_var = os.getenv(key)
        if not env_var:
            return default
        return env_var

    def _parse_id_list(self, env_var_value):
        if not env_var_value:
            return []
        
        try:
            ids = [int(id_str.strip()) for id_str in env_var_value.split(',') if id_str.strip()]
            return ids
        except ValueError as e:
            logging.error(f'Invalid ID format in environment variable: {e}')
            return []

    def __init__(self):
        # set the logging stuff
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO)

        # set env vars
        self.telegram_token = self._validate('TELEGRAM_TOKEN')
        
        # parse allowed user IDs (optional)
        allowed_users_str = self._validate_optional('ALLOWED_USER_IDS')
        self.allowed_user_ids = self._parse_id_list(allowed_users_str)
        
        # parse summary group IDs (optional)
        summary_groups_str = self._validate_optional('SUMMARY_GROUP_IDS', '-1001467780714')
        self.summary_group_ids = self._parse_id_list(summary_groups_str)
        
        # log configuration
        if self.allowed_user_ids:
            logging.info(f"Bot access restricted to user IDs: {self.allowed_user_ids}")
        else:
            logging.info("Bot access open to all users")
            
        logging.info(f"Summary feature enabled for group IDs: {self.summary_group_ids}")
