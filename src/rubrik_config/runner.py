import importlib
import inspect
import json
import logging
import os
import sys
from datetime import datetime

import cli_ui
import rubrik_cdm
import toposort
from toposort import toposort_flatten

from rubrik_config import *
from rubrik_config.helpers import ask_or_default, config_class, config_name, status_color


class Runner:

    def __init__(self, path):
        self.path = path
        self.restore_log_path = '.restore_log'

        self.rubrik = None


    def backup(self):
        if not self.rubrik:
            creds = self._read_credentials()
            self._connect(creds)

        # Create the backup dir
        backup_dir = os.path.join(
            self.path, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        os.makedirs(backup_dir, exist_ok=True)

        # Log to file and store it together with the backup
        fh = logging.FileHandler(f"{backup_dir}/output.log")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
        logging.getLogger().addHandler(fh)

        for m in self._config_modules():
            klass = config_class(m)
            klass(backup_dir, self.rubrik, logging.getLogger()).backup()

        # Remove the backup specific logger
        logging.getLogger().removeHandler(fh)

        cli_ui.info('Backup log written to:', cli_ui.turquoise, f'{backup_dir}/output.log')


    def restore(self):
        if not self.rubrik:
            creds = self._read_credentials(ignore_stored=True)
            self._connect(creds)

        # Find the backups/folders found under the given path
        backups = [d for d in os.listdir(self.path)
                   if os.path.isdir(os.path.join(self.path, d))]

        # TODO: verify that the folders are really backup folders of this tool

        choice = cli_ui.ask_choice("Which backup to restore?", choices=backups)

        logging.info('Restoring `{}`'.format(choice))

        # Create a list of config types backed up in the chosen folder
        config_types = [d for d in os.listdir(os.path.join(self.path, choice))
                        if os.path.isdir(os.path.join(self.path, choice, d))]

        # Create a list of dependencies for each config type so we can make sure
        # we restore them in a dependencies first order
        deps = {}
        for c in config_types:
            klass = config_class(c)
            instance = klass(self.path, self.rubrik, logging.getLogger())
            deps[c] = instance.dependencies

        try:
            # Topologically sort the dependencies
            sorted_config_types = toposort_flatten(deps)

            # Execute restore in the sorted order
            jobs = []
            for c in sorted_config_types:
                klass = config_class(c)
                instance = klass(self.path, self.rubrik, logging.getLogger())

                path = os.path.join(self.path, choice, config_name(instance))
                items = []
                for f in os.listdir(path):
                    with open(os.path.join(path, f), 'r') as jf:
                        items.append(json.load(jf))
                
                jobs += instance.restore(items)

            # Write the restore log
            self._write_restore_log(choice, jobs)
            
        except toposort.CircularDependencyError as e:
            logging.critical(e)


    def status(self):
        if not (os.path.exists(self.restore_log_path) and os.path.isfile(self.restore_log_path)):
            cli_ui.warning('No restore log found!')
            sys.exit(0)  # FIXME: Don't exit, rather throw an exception

        restore_log = self._get_restore_log()

        if not self.rubrik:
            creds = self._read_credentials(ignore_stored=True, presets={'address': restore_log['cluster']['ip']})
            self._connect(creds)

        statuses = []

        for job in restore_log['jobs']:
            klass = config_class(job['configType'])
            status = klass(self.path, self.rubrik, logging.getLogger()).status(job)
            if status:
                statuses.append(status)

        status_rows = list(map(
            lambda s: [
                (status_color(s[0]), s[0]),
                (cli_ui.lightgray, s[1]),
                (cli_ui.lightgray, s[2]),
                (cli_ui.lightgray, s[3]),
                (cli_ui.bold, s[4])],
            statuses
        ))

        cli_ui.info('\nBackup Id:', cli_ui.turquoise, restore_log['backupId'], end='\n\n')
        cli_ui.info_table(status_rows, headers=['Status', 'Start time', 'End time', 'Type', 'Name'])


    # Private methods

    def _read_credentials(self, path='~/.config/rubrik/cred.json', ignore_stored=False, presets={}):
        file_name = os.path.expanduser(path)
        creds = None

        if not ignore_stored:
            # Reusing the environment variable names used by python sdk, even thou they don't
            # follow conventions of all capital names
            if all(k in os.environ.keys() for k in ('rubrik_cdm_node_ip', 'rubrik_cdm_token')):
                creds = {
                    'address': os.environ['rubrik_cdm_node_ip'],
                    'api_token': os.environ['rubrik_cdm_token']
                }
                logging.info(f'Credentials read from the environment')
            else:
                # Try to read the credentials stored in the cred file instead
                try:
                    with open(file_name, 'r') as json_data:
                        creds = json.load(json_data)

                    logging.info(f"Credentials read from '{file_name}'")

                except FileNotFoundError:
                    pass

        if not creds:
            address = ask_or_default('address', 'Rubrik Cluster IP/Address', presets)
            api_token = ask_or_default('api_token', 'Rubrik API Token', presets)

            creds = {
                'address': address, 
                'api_token': api_token
            }

            #if not ignore_stored:
            #    dir_name = os.path.dirname(file_name)
            #    if not os.path.exists(dir_name):
            #        os.makedirs(dir_name)
            #
            #    with open(file_name, 'w') as creds_file:
            #        creds_file.write(json.dumps(creds, indent=4))
            #
            #    logging.info(f'Credentials saved to file {file_name}')

        return creds


    def _connect(self, creds):
        try:
            print()
            cli_ui.info('Connecting to Rubrik Cluster', cli_ui.turquoise, creds['address'])
            rbk = rubrik_cdm.Connect(node_ip=creds['address'], api_token=creds['api_token'])
            
            cluster_version = rbk.cluster_version()
            cli_ui.info('Cluster Version =', cli_ui.turquoise, cluster_version)

        except rubrik_cdm.exceptions.APICallException as e:
            cli_ui.error(e)
            sys.exit(1)  # FIXME: Replace with exception
        
        self.rubrik = rbk


    def _config_modules(self):
        all_config_modules = inspect.getmembers(
            importlib.import_module('rubrik_config'),
            lambda m: inspect.ismodule(m)
        )

        config_modules = []
        for module in all_config_modules:
            classes = inspect.getmembers(importlib.import_module(module[1].__name__), inspect.isclass)
            if len(classes) > 1 and 'RubrikConfigBase' in list(map(lambda c: c[0], classes)):
                config_modules.append(module[0])

        return config_modules


    def _write_restore_log(self, backupId, jobs):
        job_log = {
            'backupId': backupId,
            'createdOn': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z'),
            'cluster': {
                'name': self.rubrik.get('v1', '/cluster/me')['name'],
                'ip': self.rubrik.cluster_node_ip()[0],
                'version': self.rubrik.cluster_version()
            },
            'jobs': jobs
        }
        with open(self.restore_log_path, 'w') as f:
            f.write(json.dumps(job_log, indent=4, sort_keys=False))


    def _get_restore_log(self):
        f = open(self.restore_log_path, 'r')
        return json.load(f)
