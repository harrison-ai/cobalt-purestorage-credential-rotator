""" Logging Utils Module """

import json
import sys
import traceback


def format_stacktrace():
    """Format a stacktrace into a json structure
    to prevent multi-line error messages
    """

    exception_type, exception_value, exception_traceback = sys.exc_info()
    traceback_string = traceback.format_exception(
        exception_type, exception_value, exception_traceback
    )
    err_msg = json.dumps(
        {
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string,
        }
    )

    return err_msg
