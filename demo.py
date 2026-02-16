from src.logger import logging
from src.exception import MyException
import sys

logging.info("This is an info message.")

# Raising an exception to demonstrate the custom exception handling
try:
    raise ValueError("This is a test error.")
except Exception as e:
    from src.exception import MyException
    raise MyException("An error occurred in the demo script.", sys) from e