from setuptools import setup

setup(
    name='scte35-python',
    version='0.0.1-SNAPSHOT',
    packages=['scte35'],
    url='',
    license='MIT License',
    author='spsandiford',
    description='A python 3 parser library for SCTE-35 objects',
    install_requires=[
        'bitstring',
    ],
    python_requires='>=3.5',
    setup_requires=["pytest-runner",],
    tests_require=["pytest",]
)
