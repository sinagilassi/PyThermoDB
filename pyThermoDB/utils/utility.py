

def isNumber(value):
    try:
        # Check if the variable is an int or a float
        if isinstance(value, (int, float)):
            return True
        else:
            return False
    except Exception:
        return False