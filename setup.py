import setuptools

setuptools.setup(
    name="pyautosplit",
    version="0.8.0",
    author="Christoph Stahl",
    author_email="christoph.stahl@tu-dortmund.de",
    description="A python autosplit module for linux and the livesplit server module",
    url="https://github.com/christofsteel/pyautosplit.git",
    packages=setuptools.find_packages(),
    install_requires=["flask", "gevent-websockets",
                      "python-ptrace", "simpleeval", "threading"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Debuggers",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['pyautosplit=pyautosplit.main:main']
    }
)
