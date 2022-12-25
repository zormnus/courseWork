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


def check_state_number(state_number: str) -> bool:
    pattern = r"^[А-Я]\d{3}[А-Я]{2}"
    result = re.match(pattern=pattern, string=state_number)
    if result is None:
        return False
    return result.end() - result.start() == len(state_number)


def check_tech_passport(tech_passport: str) -> bool:
    pattern = r"^[\d]{2} [\А-Я]{2} [\d]{6}"
    result = re.match(pattern=pattern, string=tech_passport)
    if result is None:
        return False
    return result.end() - result.start() == len(tech_passport)
