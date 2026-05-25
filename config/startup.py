import os


def should_run_startup_migrations():
    value = os.environ.get('RUN_MIGRATIONS_ON_STARTUP')
    if value is not None:
        return value.lower() == 'true'
    return bool(os.environ.get('RENDER'))


def run_startup_migrations():
    if not should_run_startup_migrations():
        return

    import django
    from django.core.management import call_command

    django.setup()
    call_command('migrate', interactive=False, verbosity=1)
