import datetime
import json
import os

import rubrik_cdm
from rubrik_config.rubrik_config_base import RubrikConfigBase
from rubrik_config.helpers import filter_fields, config_name
from urllib.parse import urlencode


class SlaDomainConfig(RubrikConfigBase):

    def __init__(self, path, rubrik, logger):
        super().__init__(path, rubrik, logger)

        self.dependencies = { 'archival_location', 'replication_target' }


    def backup(self):
        response = self.rubrik.get('v2', '/sla_domain?{}'.format(urlencode({'primary_cluster_id': 'local'})))
        self.logger.info("%s SLA domains found!" % response['total'])

        sla_domains = response['data']

        self._write(sla_domains, self.config_name)

        return response['total']


    def restore(self, items):
        jobs = []

        for item in items:
            config = filter_fields(item['config'], [
                'name',
                'frequencies',
                'allowedBackupWindows',
                'logConfig',
                'firstFullAllowedBackupWindows',
                'localRetentionLimit',
                'isRetentionLocked'
                'archivalSpecs',
                'replicationSpecs',
                'showAdvancedUi',
                'advancedUiConfig'
            ])

            # FIXME: Restore archivalSpecs and replicationSpecs correctly!
            
            self.logger.info("Restoring sla domain `{}`".format(config['name']))
            
            try:
                response = self.rubrik.post('v2', '/sla_domain', config)
                created_on = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z')
                jobs += ({ 
                    'id': response['id'], 
                    'type': 'CREATE_SLA_DOMAIN', 
                    'name': config['name'], 
                    'createdOn': created_on,
                    'configType': self.config_name
                }, )

                # TODO: How is uiColor and isDefault restored?
                # TODO: If isPaused is true, execute a pause request after creation

            except rubrik_cdm.exceptions.APICallException as e:
                self.logger.error(e)

        return jobs


    def status(self, job):
        job_status = None

        if 'CREATE_SLA_DOMAIN' == job['type']:
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
