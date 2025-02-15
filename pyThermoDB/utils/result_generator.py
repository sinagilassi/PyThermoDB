# GENERATE RESULTS


def format_eq_data(value: float | str, res_dict: dict, message: str) -> dict:
    """
    Format the equation result data.

    Parameters
    ----------
    value : float or None
        The calculated value.
    res_dict : dict
        Dictionary of the result data.
    message : str
        Custom message for the calculation.

    Returns
    -------
    eq_data : dict
        Formatted equation result data.
    """
    return {'value': value, **res_dict, 'message': message}
