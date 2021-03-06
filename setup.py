from setuptools import setup

setup(
    name='router',
    version='0.0.2',
    description='A module-extensible message router',
    author='Nathan Latchaw',
    author_email='natelatchaw@gmail.com',
    license='Creative Commons',
    packages=[
        'router',
        'router.configuration',
        'router.packaging',
    ],
    package_data={
        "router": [
            "py.typed"
        ],
        "router.configuration": [
            "py.typed"
        ],
        "router.packaging": [
            "py.typed"
        ],
    },
    url='not available',
    install_requires=[],
    classifiers=[
        'Development Status :: Alpha',
        'Intended Audience :: Hobbyist',
        'Operating System :: Agnostic',
        'Programming Language :: Python :: 3.10',
    ],
)