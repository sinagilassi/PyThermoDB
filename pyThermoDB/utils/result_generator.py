# GENERATE RESULTS
import numpy as np
from ..models import EquationResult

def format_eq_data(value: float | str | dict | np.ndarray, res_dict: dict, message: str) -> EquationResult:
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
    eq_data : EquationResult
        Formatted equation result data.
    """
    try:
        # set
        eq_data_ = {'value': value, **res_dict, 'message': message}
        # set
        eq_data = EquationResult(**eq_data_)
    
        return eq_data
    except Exception as e:
        raise Exception(f"Error formatting equation data: {e}") from e
