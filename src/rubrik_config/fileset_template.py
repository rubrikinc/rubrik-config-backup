import datetime
import json
import os
from urllib.parse import urlencode

import rubrik_cdm
from rubrik_config.helpers import filter_fields, config_name
from rubrik_config.rubrik_config_base import RubrikConfigBase


class FilesetTemplateConfig(RubrikConfigBase):

    def __init__(self, path, rubrik, logger):
        super().__init__(path, rubrik, logger)
        

    def backup(self):
        response = self.rubrik.get('v1', '/fileset_template?{}'.format(urlencode({'primary_cluster_id': 'local'})))
        self.logger.info("%s Fileset Templates found!" % response['total'])

        fileset_templates = response['data']
        
        self._write(fileset_templates, self.config_name)

        return response['total']


    def restore(self, items):
        jobs = []

        for item in items:
            config = filter_fields(item['config'], [
                'name',
                'excludes',
                'includes',
                'useWindowsVss',
                'exceptions',
                'allowBackupNetworkMounts',
                'allowBackupHiddenFoldersInNetworkMounts',
                'operatingSystemType',
                'shareType',
                'preBackupScript',
                'postBackupScript',
                'backupScriptTimeout',
                'backupScriptErrorHandling',
                'isArrayEnabled'
            ])

            self.logger.info("Restoring fileset template `{}`".format(config['name']))
            
            try:
                response = self.rubrik.post('v1', '/fileset_template', config)
                created_on = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z')
                jobs += ({ 
                    'id': response['id'], 
                    'type': 'CREATE_FILESET_TEMPLATE', 
                    'name': config['name'], 
                    'createdOn': created_on,
                    'configType': self.config_name
                }, )
            
            except rubrik_cdm.exceptions.APICallException as e:
                self.logger.error(e)

        return jobs


    def status(self, job):
        job_status = None

        if 'CREATE_FILESET_TEMPLATE' == job['type']:
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
