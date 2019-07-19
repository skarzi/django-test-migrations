import os
import sys


def pytest_addoption(parser):
    parser.addoption(
        '--no-pkgroot',
        action='store_true',
        default=False,
        help=(
            'Remove package root directory from sys.path, ensuring that '
            'rest_framework is imported from the installed site-packages. '
            'Used for testing the distribution.'
        ),
    )


def pytest_configure(config):
    from django.conf import settings

    settings.configure(
        DEBUG_PROPAGATE_EXCEPTIONS=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        SECRET_KEY='not very secret in tests',
        INSTALLED_APPS=(
            # 'django.contrib.sites',
            # 'test_migrations',
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ),
    )

    if config.getoption('--no-pkgroot'):
        sys.path.pop(0)

        # import `test_migrations` before pytest re-adds the package
        # root directory.
        import test_migrations
        package_dir = os.path.join(os.getcwd(), 'test_migrations')
        assert not test_migrations.__file__.startswith(package_dir)
