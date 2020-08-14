import abc
import json
import os

from rubrik_config import helpers


class RubrikConfigBase(abc.ABC):

    def __init__(self, path, rubrik, logger):
        self.path = path
        self.rubrik = rubrik
        self.logger = logger

        self.cluster_version = self.rubrik.cluster_version()
        self.cluster_name = helpers.cluster_name(self.rubrik)

        self.config_name = helpers.config_name(self)
        self.dependencies = set()


    @abc.abstractmethod
    def backup(self):
        """Backup all configuration items of this type.

        Returns:
            int: The number of items backed up.
        """
        pass


    @abc.abstractmethod
    def restore(self, items):
        """Restore the given configuration items.

        Args:
            items ([str]): The configuration items to restore.

        Returns:
            list: A list of jobs that have been initiated on the cluster as part
                  of the recovery of the configuration.
        """
        pass


    @abc.abstractmethod
    def status(self, job):
        """Return the status of the given job.

        Args:
            job (str): Job ID

        Returns:
            list: A list containing the status details of the given job.
        """
        pass


    # Private Methods

    def _write(self, content, content_type, name_fn=lambda x: x['name']):
        if len(content) == 0:
            return

        content_dir_name = content_type.split('.')[0]
        path = f"{self.path}/{content_dir_name}"
        os.makedirs(path, exist_ok=True)
        
        for item in content:
            filename = f"{path}/{helpers.secure_filename(name_fn(item))}.json"
            with open(filename, 'w') as f:
                file_content = { 
                    'clusterName': self.cluster_name, 
                    'clusterVersion': self.cluster_version, 
                    'type': content_type,
                    'config': item
                }
                f.write(json.dumps(file_content, indent=4, sort_keys=True))

            self.logger.info("'%s' successfully saved to %s" % (name_fn(item), filename))
