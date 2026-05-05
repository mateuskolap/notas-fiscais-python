from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class StrValidator(str):
    @classmethod
    def _validate(cls, value: Any) -> str:
        raise NotImplementedError('You must implement _validate method')

    @classmethod
    def __get_pydantic_core_schema__(  # noqa: PLW3201
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ):
        return core_schema.no_info_after_validator_function(
            cls._validate, core_schema.str_schema()
        )


PASSWORD_SPECIAL_CHARS: set[str] = {
    '@',
    '#',
    '%',
    '!',
    '&',
    '*',
    '(',
    ')',
    '_',
    '+',
    '=',
    '{',
    '}',
    '[',
    ']',
    '.',
}

PASSWORD_MIN_LENGTH: int = 8
PASSWORD_MAX_LENGTH: int = 20
PASSWORD_INCLUDES_SPECIAL_CHARS: bool = True
PASSWORD_INCLUDES_NUMBERS: bool = True
PASSWORD_INCLUDES_LOWERCASE: bool = True
PASSWORD_INCLUDES_UPPERCASE: bool = True


class PasswordStr(StrValidator):
    @classmethod
    def _validate(cls, value: str) -> str:
        if not PASSWORD_MIN_LENGTH <= len(value) <= PASSWORD_MAX_LENGTH:
            raise ValueError(
                f'Password length should be at least {PASSWORD_MIN_LENGTH} and at most {PASSWORD_MAX_LENGTH} characters'  # noqa: E501
            )

        has_upper = has_lower = has_digit = has_special = False

        for char in value:
            if char.isupper():
                has_upper = True
            elif char.islower():
                has_lower = True
            elif char.isdigit():
                has_digit = True
            elif char in PASSWORD_SPECIAL_CHARS:
                has_special = True

        if PASSWORD_INCLUDES_NUMBERS and not has_digit:
            raise ValueError('Password should have at least one numeral')
        if PASSWORD_INCLUDES_UPPERCASE and not has_upper:
            raise ValueError('Password should have at least one uppercase letter')
        if PASSWORD_INCLUDES_LOWERCASE and not has_lower:
            raise ValueError('Password should have at least one lowercase letter')
        if PASSWORD_INCLUDES_SPECIAL_CHARS and not has_special:
            raise ValueError(
                f'Password should have at least one symbol: {PASSWORD_SPECIAL_CHARS}'
            )

        return value
