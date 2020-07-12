import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rubrik-config-backup", 
    version="0.5",
    author="Ramzi Ferchichi",
    author_email="ramzi.ferchichi@rubrik.com",
    description="Backup and restore of Rubrik cluster configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rubrikinc/rubrik-config-backup",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    scripts=['scripts/rbkcb']
)
