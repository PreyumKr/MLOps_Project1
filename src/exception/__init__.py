import sys
import logging

def error_message_detail(error: Exception, error_detail) -> str:
    try:
        exc_info = None
        if hasattr(error_detail, "exc_info"):
            exc_info = error_detail.exc_info()
        # exc_info may be None or return (None, None, None) when no exception is active
        if exc_info and len(exc_info) == 3 and exc_info[2] is not None:
            exc_tb = exc_info[2]
            file_name = exc_tb.tb_frame.f_code.co_filename
            line_number = exc_tb.tb_lineno
        else:
            # Try to get traceback from the error object itself if present
            tb = getattr(error, "__traceback__", None)
            if tb is not None:
                file_name = tb.tb_frame.f_code.co_filename
                line_number = tb.tb_lineno
            else:
                file_name = "Not available"
                line_number = "Not available"

        error_message = f"Error occurred in python script: [{file_name}] at line number [{line_number}]: {str(error)}"
        logging.error(error_message)
        return error_message
    except Exception:
        # Fallback message if anything goes wrong while preparing the error message
        fallback = f"Error occurred but traceback is not available: {str(error)}"
        logging.error(fallback)
        return fallback


class MyException(Exception):
    def __init__(self, error_message, error_detail):
        super().__init__(str(error_message))
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self) -> str:
        return self.error_message