import os


def mod_directory():
    path = os.path.abspath(__file__)
    while path and not path.lower().endswith('.ts4script'):
        parent = os.path.dirname(path)
        if parent == path:
            return os.path.dirname(os.path.abspath(__file__))
        path = parent
    return os.path.dirname(path)


def config_path():
    return os.path.join(mod_directory(), 'BeefyBoyos.ini')


def log_path():
    return os.path.join(mod_directory(), 'BeefyBoyos.log')
