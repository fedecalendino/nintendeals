def format_float(value, total_digits=0):
    value = "%.2f" % value

    return "0" * (total_digits - len(value)) + value
