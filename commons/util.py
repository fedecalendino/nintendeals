def format_float(value, total_digits=0):
    value = '%.2f' % value
    zeroes_to_add = total_digits - len(value) if total_digits > len(value) else 0

    return '{}{}'.format('0' * zeroes_to_add, value)
