import datetime
import json
import os
import sys

import cli_ui
import rubrik_cdm

from urllib.parse import urlencode
from rubrik_config.rubrik_config_base import RubrikConfigBase

from rubrik_config.helpers import config_name, ask_multiline_string


class ArchivalLocationConfig(RubrikConfigBase):

    def __init__(self, path, rubrik, logger):
        super().__init__(path, rubrik, logger)


    def backup(self):
        object_store_locations_response = self._get_object_store_locations()
        nfs_locations_response = self._get_nfs_locations()
        
        total_locations = object_store_locations_response['total'] + nfs_locations_response['total']

        self.logger.info("%s Archival locations found!" % total_locations)

        self._write(object_store_locations_response['data'], self.config_name+'.object_store', lambda x: x['definition']['name'])
        self._write(nfs_locations_response['data'], self.config_name+'.nfs', lambda x: x['definition']['name'])

        return total_locations


    def restore(self, items):
        jobs = []

        for item in items:
            try:
                item_type = item['type'].split('.')[1]
                
                self.logger.info("Restoring archival location `{}`".format(item['config']['definition']['name']))

                if 'object_store' == item_type:
                    jobs += (self._add_object_store_location(item['config']), )
                elif 'nfs' == item_type:
                    jobs += (self._add_nfs_location(item['config']), )
                elif 'qstar' == item_type:
                    jobs += (self._add_qstar_location(item['config']), )
                else:
                    self.logger.error("Unrecognized archival location type '{}'".format(item_type))

            except rubrik_cdm.exceptions.APICallException as e:
                self.logger.error(e)

        return jobs


    def status(self, job):
        job_status = None

        if 'ADD_OBJECT_STORE' == job['type'] or 'ADD_NFS_SHARE' == job['type']:
            response = self.rubrik.get('internal', '/archive/location/job/connect/{}'.format(job['id']))
            end_time = ''
            if 'endTime' in response.keys():
                end_time = response['endTime']

            job_status = [
                response['status'],
                response['startTime'],
                end_time,
                job['type'],
                job['name']
            ]

        return job_status


    # Private methods

    def _get_object_store_locations(self):
        return self.rubrik.get('internal', '/archive/object_store')


    def _get_nfs_locations(self):
        return self.rubrik.get('internal', '/archive/nfs')


    def _get_qstar_locations(self):
        raise NotImplementedError


    def _get_dca_locations(self):
        raise NotImplementedError


    def _add_object_store_location(self, config):
        if 'Azure' == config['definition']['objectStoreType']:
            config['definition']['secretKey'] = cli_ui.ask_password('Access Key')
            config['definition']['pemFileContent'] = ask_multiline_string('RSA Key').strip()

        # TODO: Handle S3 archives!

        response = self.rubrik.post('internal', '/archive/object_store', config['definition'], timeout=120)
        created_on = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z')

        return {
            'id': response['jobInstanceId'],
            'type': 'ADD_OBJECT_STORE',
            'name': config['definition']['name'],
            'createdOn': created_on,
            'configType': self.config_name
        }


    def _add_nfs_location(self, config):
        encryption_password = cli_ui.ask_password('Encryption Password (leave blank to disable)')
        if not encryption_password.strip():
            config['definition']['disableEncryption'] = True
        else:
            config['definition']['encryptionPassword'] = encryption_password

        response = self.rubrik.post('internal', '/archive/nfs', config['definition'], timeout=120)
        created_on = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S%z')

        return {
            'id': response['jobInstanceId'],
            'type': 'ADD_NFS_SHARE',
            'name': config['definition']['name'],
            'createdOn': created_on,
            'configType': self.config_name
        }
    
    
    def _add_qstar_location(self, config):
        pass


    def _add_dca_location(self, config):
        raise NotImplementedError
