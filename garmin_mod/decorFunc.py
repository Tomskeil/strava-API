#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module incorporates the wrapper function which shall be used
as decorators for specific modules
"""

__author__ = "Thomas Keil"
__email__ = "tomskeil@hotmail.com"

__license__ = "GPL"
__version__ = "0.0.0"
__maintainer__ = "Thomas Keil"
__status__ = "Prototype"

# Import packages
from functools import wraps
import time


# Retry wrapper
def retry_request(retry_count, errorCallback):
    def outside_func(func):
        @wraps(func)
        def inside_func(self, *args, **kwargs):
            for i in range(1, retry_count+1):
                if i < retry_count:
                    func_name = func.__code__.co_name
                    func_name = func_name.replace("fetch_", "")
                    print("Fetching {fn}: attempt {rc}".format(fn=func_name,
                                                               rc=i))

                    result = func(self, *args, **kwargs)

                    if result.status_code == 401:
                        """ Unauthorised request """
                        print("Unauthorised request - retrying...")
                        time.sleep(1)
                        ExceptionFunc = getattr(self, errorCallback)
                        ExceptionFunc()

                    else:
                        print("Successfully retrieved {fn} data".format(fn=func_name))
                        break

                else:
                    print("Request limit exceeded - no further requests")

            return result
        return inside_func
    return outside_func
