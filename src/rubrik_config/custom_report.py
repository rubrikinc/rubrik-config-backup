import datetime
import json
import os

import rubrik_cdm
from urllib.parse import urlencode

from rubrik_config.rubrik_config_base import RubrikConfigBase
from rubrik_config.helpers import config_name, filter_fields


class CustomReportConfig(RubrikConfigBase):

    def __init__(self, path, rubrik, logger):
        super().__init__(path, rubrik, logger)


    def backup(self):
        response = self.rubrik.get('internal', '/report?report_type=Custom&primary_cluster_id=local')
        self.logger.info("%s Custom Reports found!" % response['total'])

        for item in response['data']:
            self._write([self.rubrik.get('internal', '/report/{}'.format(item['id']))], self.config_name)

        return response['total']


    def restore(self, items):
        jobs = []

        for item in items:
            config = filter_fields(item['config'], [
                'name',
                'reportType',
                'reportTemplate',
                'chart0',
                'chart1',
                'table'
                'filters'
            ])

            self.logger.info("Restoring custom report `{}`".format(config['name']))
            
            try:
                response = self.rubrik.post('internal', '/report', config, timeout=120)
                created_on = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z')
                jobs += ({ 
                    'id': response['id'], 
                    'type': 'CREATE_CUSTOM_REPORT', 
                    'name': config['name'], 
                    'createdOn': created_on,
                    'configType': self.config_name
                }, )
            
            except rubrik_cdm.exceptions.APICallException as e:
                self.logger.error(e)

        return jobs


    def status(self, job):
        job_status = None

        if 'CREATE_CUSTOM_REPORT' == job['type']:
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