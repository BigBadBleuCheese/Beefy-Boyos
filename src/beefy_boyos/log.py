import time

from beefy_boyos import paths

_started = False


def write(message):
    global _started
    try:
        with open(paths.log_path(), 'a' if _started else 'w', encoding='utf-8') as file:
            file.write('{} {}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), message))
        _started = True
    except OSError:
        pass
