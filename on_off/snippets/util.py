import ssl
import json
import urllib.request
import re
def validate_phone_number(phone_numbers):
    for num in phone_numbers:
        pattern = r'^1[3456789]\d{9}$'
        match = re.match(pattern, str(num))
        if match:
            pass
        else:
            return False
    return True
