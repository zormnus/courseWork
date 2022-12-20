import re


def check_email(email: str) -> bool:
    pattern = r"(.+)@([.\w]+)\.(\w+)"
    result = re.match(pattern=pattern, string=email)
    if result is None:
        return False
    return result.end() - result.start() == len(email)


def check_phone_number(phone_number: str) -> bool:
    pattern = r"\+7(\d{10})"
    result = re.match(pattern=pattern, string=phone_number)
    if result is None:
        return False
    return result.end() - result.start() == len(phone_number)
