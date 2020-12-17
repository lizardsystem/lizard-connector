from setuptools import setup

version = '0.7.3'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'setuptools',
    ],

tests_require = [
    'coverage',
    'mock',
    'nose',
    ]

setup(name='lizard-connector',
      version=version,
      description="A connector to connect to the Lizard-API with Python.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Topic :: Software Development :: Libraries :: Application Frameworks'
      ],
      keywords=['lizard', 'rest', 'interface', 'api'],
      author='Roel van den Berg',
      author_email='roel.vandenberg@nelen-schuurmans.nl',
      url='http://demo.lizard.net',
      license='GPL',
      packages=['lizard_connector'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
          ]},
      )
