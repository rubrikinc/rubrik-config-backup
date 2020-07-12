import datetime
import json
import os

import cli_ui
import rubrik_cdm

from rubrik_config.rubrik_config_base import RubrikConfigBase
from rubrik_config.helpers import config_name, filter_fields, ask_multiline_string
from urllib.parse import urlencode


class ReplicationTargetConfig(RubrikConfigBase):

    def __init__(self, path, rubrik, logger):
        super().__init__(path, rubrik, logger)


    def backup(self):
        response = self.rubrik.get('internal', '/replication/target')
        self.logger.info("%s Replication Targets found!" % response['total'])

        replication_targets = response['data']
        self._write(replication_targets, self.config_name, lambda x: x['targetClusterName'])

        return response['total']


    def restore(self, items):
        jobs = []

        for item in items:
            self.logger.info("Restoring replication target `{}`".format(item['config']['targetClusterName']))

            config = filter_fields(item['config'], [
                'targetClusterAddress',
                'targetGateway',
                'sourceGateway',
                'replicationSetup'
            ])

            username = cli_ui.ask_string('Username')
            password = cli_ui.ask_password('Password')
            ca_certs = ask_multiline_string('Trusted Root Certificate').strip()
            realm = cli_ui.ask_string('Realm')

            config['username'] = username
            config['password'] = password
            if ca_certs:
                config['caCerts'] = ca_certs
            if realm:
                config['realm'] = realm
            
            try:
                response = self.rubrik.post('internal', '/replication/target', config, timeout=120)
                created_on = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z')
                jobs += ({ 
                    'id': response['id'], 
                    'type': 'ADD_REPLICATION_TARGET', 
                    'name': response['targetClusterName'], 
                    'createdOn': created_on,
                    'configType': self.config_name
                }, )

            except rubrik_cdm.exceptions.APICallException as e:
                self.logger.error(e)

        return jobs


    def status(self, job):
        job_status = None

        if 'ADD_REPLICATION_TARGET' == job['type']:
            status = 'SUCCEEDED'
            start_time = job['createdOn']
            end_time = job['createdOn']

            job_status = [
                status,
                start_time,
                end_time,
                job['type'],
                job['name']
            ]

        return job_status
