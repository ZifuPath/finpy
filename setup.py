from setuptools import setup, find_packages

setup(
    name='finpy',
    version='0.1.0',
    packages=find_packages(),
    description='For Fetching Data From NSE APIs',
    long_description_content_type="text/markdown",
    install_requires=[
        'pandas',
        'requests',
        'pydantic',
    ],
    entry_points={
        'console_scripts': [
            'your-command-name=finpy.module_name:main',
        ],
    },
    author='zorif',
    author_email='fzpathan1008@gamil.com',
    maintainer='Your Name',
    maintainer_email='fzpathan1008@gmail.com',
    url='www.finman.pro'
)
