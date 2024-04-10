from setuptools import setup

setup(name='ml_runlog',
      version='2.0',
      description='Simple script to log experiments to Google Sheets. Version 2.0 is cleaner, has a class based structure and supports logging multiple rows at once.',
      url='https://github.com/anag004/ml-runlog',
      author='Ananye Agarwal',
      author_email='ananayagarwal@gmail.com',
      license='MIT',
      packages=['ml_runlog'],
      install_requires=[
          'pygsheets',
          'pandas'
      ],
      zip_safe=False)