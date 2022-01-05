from setuptools import setup

setup(name='ml_runlog',
      version='1.0',
      description='Simple script to log experiments to Google Sheets',
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