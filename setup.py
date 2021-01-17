import setuptools

setuptools.setup(
    name="v6as4l",
    version="0.0.1",
    author="Christoph Stahl",
    author_email="christoph.stahl@tu-dortmund.de",
    description="A very rudamentary implementation of an auto splitter for the game VVVVVV for linux",
    url="https://github.com/christofsteel/v6as4l.git",
    packages=setuptools.find_packages(),
    install_requires=["python-ptrace"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Debuggers",
    ],
    python_requires='>=3.7',
    entry_points = {
        'console_scripts': ['v6as4l=v6as4l.main:main']
    }
)
