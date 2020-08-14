# Rubrik Configuration Backup

## Overview

This tool provide backup and restore of the following Rubrik cluster configuration items:

* SLA Domains
* Archival Locations
* Replication Targets
* Fileset Templates
* Custom Report templates

## Installation

```
$ git clone https://github.com/rubrikinc/rubrik-config-backup
$ cd rubrik-config-backup
$ python setup.py install
```

## Usage

````
$ rbkcb [-h] [--insecure] {backup,restore,status} path
````

