def phone_number_valid(phone_num: str) -> str:
    allowed_chars = set('0123456789+ ()-.')
    if not all(c in allowed_chars for c in phone_num):
        raise ValueError('Недопустимый ввод. В номере телефона встречаются недопустимые символы.')
    
    digits = ''.join(c for c in phone_num if c.isdigit())
    if len(digits) == 11:
        if digits.startswith('8') or digits.startswith('7'):
            if digits.startswith('7'):
                digits = '8' + digits[1:]
        else: 
            raise ValueError('Недопустимый ввод. Неверное количество цифр.')
    elif len(digits) == 10:
        digits = '8' + digits
    else:
        raise ValueError('Недопустимый ввод. Неверное количество цифр.')
    
    formatted = f'8-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}'
    return formatted