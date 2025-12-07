# import package/modules


def isNumber(value):
    try:
        # Check if the variable is an int or a float
        if isinstance(value, (int, float)):
            return True
        else:
            return False
    except Exception:
        return False


def uppercaseStringList(value):
    '''
    uppercase string list

    args:
        value: string list

    returns:
        uppercase string list
    '''
    uppercaseList = list(map(str.upper, value))
    return uppercaseList


def is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
