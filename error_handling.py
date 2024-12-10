class CustomError(Exception):
"""Base class for custom exceptions"""
pass
class ConfigError(CustomError):
"""Exception raised for errors in the configuration."""
def __init__(self, message="Configuration error occurred"):
self.message = message
super().__init__(self.message)
class ConnectionError(CustomError):
"""Exception raised for errors in network connections."""
def __init__(self, message="Connection error occurred"):
self.message = message
super().__init__(self.message)
