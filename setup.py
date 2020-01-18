import os
import re
import shutil
import sys

from setuptools import (
    find_packages,
    setup,
)

VERSION_REGEXP = re.compile(
    r"__version__ = ['\"](?P<version>[^'\"]+)['\"]",
    re.IGNORECASE,
)


def _read(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:  # pylint: disable=C0103
        return f.read()


def get_version(package: str) -> str:
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py_content = _read(os.path.join(package, '__init__.py'))
    return VERSION_REGEXP.search(init_py_content).group('version')


VERSION = get_version('test_migrations')


if sys.argv[-1] == 'publish':
    if os.system('pip freeze | grep twine'):
        print('twine not installed.\nUse `pip install twine`.\nExiting.')
        sys.exit()
    os.system('python setup.py sdist bdist_wheel')
    if os.system("twine check dist/*"):
        print('twine check failed. Packages might be outdated.')
        print('Try using `pip install -U twine wheel`.\nExiting.')
        sys.exit()
    os.system('twine upload dist/*')
    print('You probably want to also tag the version now:')
    print(
        "  git tag -a {version} -m 'version {version}'".format(
            version=VERSION,
        ),
    )
    print('  git push --tags')
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('djangotestmigrations.egg-info')
    sys.exit()


setup(
    name='djangotestmigrations',
    version=VERSION,
    url='https://github.com/skarzi/django-test-migrations',
    license='MIT',
    description="Django's migrations testing utilities",
    long_description=_read('README.md'),
    long_description_content_type='text/markdown',
    author='Łukasz Skarżyński',
    author_email='github@skarzi.com',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    package_data={'test_migrations': ['py.typed', '*.pyi']},
    install_requires=['django>=1.11'],
    python_requires='>=3.4',
    extras_require={
        'pytest': ['pytest>=4.4.0', 'pytest_django>=3.4.0'],
    },
    entry_points={
        'pytest11': [
            (
                'django_test_migrations = '
                'test_migrations.contrib.pytest_plugin.plugin [pytest]'
            ),
        ],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
