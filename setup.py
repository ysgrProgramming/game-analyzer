from setuptools import setup, find_packages

setup(
    name='game-analyzer',
    version='0.1.0',
    description='A game analyzer that returns the optimal strategy for a given game state.',
    author='ysgrProgramming',
    url='https://github.com/ysgrProgramming/game-analyzer',  # プロジェクトのURL
    packages=find_packages(exclude=('tests', 'samples')),
    install_requires=[
        'numpy',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)
