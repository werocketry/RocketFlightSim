from setuptools import setup, find_packages

setup(
    name='rocketflightsim',
    version='0.1.1',
    description='A lightweight rocket flight simulator.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Giorgio Chassikos, Western Engineering Rocketry Team',
    author_email='werocketry@gmail.com',
    url='https://github.com/werocketry/RocketFlightSim',
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT'
)