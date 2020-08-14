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
    packages=['rubrik_config'],
    package_dir={'rubrik_config': 'src/rubrik_config'},
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
    install_requires=[
        'cli-ui == 0.10.2',
        'rubrik-cdm >= 2.0.8',
        'toposort == 1.5',
    ],
    extras_require={
        'docs': [
            'Sphinx == 3.1.2',
            'recommonmark == 0.6.0',
            'pydata-sphinx-theme == 0.3.1',
        ],
    },
    scripts=['scripts/rbkcb']
)
