"""
Flask-WkHTMLtoPDF
-------------

Convert JavaScript dependent Flask templates into PDFs with wkhtmltopdf.
"""
from setuptools import setup


setup(
    name='Flask-WkHTMLtoPDF',
    version='0.1.0',
    url='https://github.com/chris-griffin/flask-wkhtmltopdf',
    license='MIT',
    author='Chris Griffin',
    author_email='cwg23@georgetown.edu',
    description='Convert JavaScript dependent Flask templates into PDFs with wkhtmltopdf.',
    long_description=__doc__,
    py_modules=['flask_wkhtmltopdf'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask','Celery'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Printing'
    ],
    test_suite='tests'
)