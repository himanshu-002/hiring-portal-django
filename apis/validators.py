from django.core.exceptions import ValidationError


def validate_alphabets_only(value: str) -> None:
    """
    validator functions for only saving string with alphabets only
    :param value: string
    :return: None
    """

    def check_allowed_chars(val: str) -> bool:
        import string

        allowed_chars = string.ascii_letters + "."
        if val.strip('" ", "."') == "":  # handles just "." and "...." so on, values
            return False
        if val.startswith(".") or val.endswith("."):
            return False
        var_list = [True for i in val.strip() if i in allowed_chars]
        return all(var_list)

    if not check_allowed_chars(value):
        raise ValidationError(
            f'{value} is a invalid, this field takes only Text values, remove numbers or special characters'
        )
