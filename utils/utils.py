def dict_filter(filter, data):
    for key, value in filter.items():
        if key not in data or data[key] != value:
            return False
    return True
