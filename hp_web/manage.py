#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# Skip cache if we don't need it
match sys.argv[-1]:
    case 'makemigrations':
        os.environ['SKIP_CACHE'] = '1'
    case 'migrate':
        os.environ['SKIP_CACHE'] = '1'
    case 'shell':
        os.environ['SKIP_CACHE'] = '1'

# Do testing if required
if '-t' in sys.argv:
    os.environ['DO_TEST'] = 'True'
    sys.argv.remove('-t')


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hp_web.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
