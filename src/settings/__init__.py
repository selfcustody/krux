def load(setting, default, strip=True):
    try:
        value = open('/sd/settings/%s.txt' % setting).read()
        if strip:
            return value.strip()
        return value
    except:
        return default
