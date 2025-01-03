def create_error_response(error_type: str, description: str):
    """
    Constructs a consistent error response.

    Args:
        error_type (str): The type of the error (e.g., VALIDATION_ERROR).
        description (str): A human-readable description of the error.
        field (str, optional): The field causing the error.
        location (str, optional): The location of the field (e.g., body, prestep).

    Returns:
        dict: A structured error response.
    """
    error_detail = {"type": error_type, "description": description}
    return error_detail
