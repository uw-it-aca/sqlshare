import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='sqlshare-web',
    version='0.1',
    packages=['sqlshare_web'],
    include_package_data=True,
    install_requires = [
        # For ansible deployments, you also need to update requirements.txt :(
        'setuptools',
        'django==1.10.*',
        'django-compressor',
        'django-templatetag-handlebars',
        'django_mobileesp',
        'sanction',
    ],
    license='Apache License, Version 2.0',  # example license
    description='Frontend for SQLShare',
    long_description=README,
    url='https://github.com/uw-it-aca/sqlshare',
    author='Your Name',
    author_email='yourname@example.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
