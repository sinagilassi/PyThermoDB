# import libs
import os
from typing import Optional
# local


def check_file_path(
    file_path: Optional[str] = None,
    default_path: Optional[str] = None,
    create_dir: bool = False
) -> str:
    """
    Check and prepare the file path.

    Parameters
    ----------
    file_path : Optional[str], optional
        The file path to check, by default None
    default_path : Optional[str], optional
        The default path to use if file_path is None, by default None
    create_dir : bool, optional
        Whether to create the directory if it does not exist, by default False

    Returns
    -------
    str
        The normalized file or directory path.
        Defaults to the current working directory if no path is provided.
    """
    # Determine the final path (fall back to default, then current dir)
    final_path = file_path or default_path or os.getcwd()

    # Normalize path (~ expansion + absolute path)
    final_path = os.path.abspath(os.path.expanduser(final_path))

    # Get directory part: if it's a file, take dirname; if it's a dir, use itself
    dir_path = os.path.dirname(final_path) if os.path.splitext(
        final_path)[1] else final_path

    # Check directory validity
    if os.path.exists(dir_path) and not os.path.isdir(dir_path):
        raise NotADirectoryError(
            f"Path exists but is not a directory: {dir_path}")

    # Create directory if requested
    if create_dir and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    return final_path
