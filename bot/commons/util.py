def format_float(value, total_digits=0):
    value = "%.2f" % value

    if total_digits == 0:
        result = value
    else:
        result = "0" * (total_digits - len(value)) + value

    if result.endswith(".00"):
        result = result.replace(".00", "")

    return result


def merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value

    return destination
