####################################################
# Lanuching jobs on Amazon EC2 
#
# File:      manysim.py
#
# Author:    Christopher M Poole,
# Email:     mail@christopherpoole.net
#
# Date:      20th March, 2011
####################################################

import os
import time
import urllib
import itertools
import tarfile
import pickle
import multiprocessing

import boto


class Configuration(object):
    """Configuration object holding AWS connection credentials."""
    
    def __init__(self, **kwargs):
        valid_kwargs = ['key_name', 'region', 'job_archive', 'file_manifest', \
            'job_config', 'output_archive', 'output_files', 'spot_price',
            'bucket_name']
        required_kwargs = ['access_key', 'secret_key', 'instance_type', \
            'instance_image', 'instance_count', 'spot', 'pool_size', 'job_file']
        
        for k, v in kwargs.iteritems():
            assert k in valid_kwargs or k in required_kwargs, \
                "Invalid keyword argument %s" % k
            setattr(self, k, v)
        
        for k in required_kwargs:
            assert hasattr(self, k), "Keyword argument %s must be provided" % k
        
                
class Store(object):
    """The Store for staging of the job and data on AWS S3."""
    
    def __init__(self, configuration):
        self._config = configuration
        
        self._conn = boto.connect_s3(aws_access_key_id=self._config.access_key,
            aws_secret_access_key=self._config.secret_key)
        self._bucket = self._conn.get_bucket(self._config.bucket_name)
    
    def push(self, local_target, remote_target, overwrite=False):
        assert os.path.exists(local_target), \
            "Local target file does not exist at %s" % local_target
        
    	key = self._bucket.get_key(remote_target)
    	if key is None:
    	    key = self._bucket.new_key(remote_target)
    	else:
    	    assert overwrite is True, \
    	        "Remote target file exist, overwrite=True to force."
        key.set_contents_from_file(file(local_target, 'r'))
            
    def pull(self, remote_target, local_target, overwrite=False):
        if overwrite is False:
            assert not os.path.exists(local_target), \
                "Local target file exist, overwrite=True to force."
 
    	key = self._bucket.get_key(remote_target)
    	assert key is not None, \
    	    "Remote target does not exist at %s" % remote_target
    	key.get_contents_to_file(file(local_target, 'w'))

    def exists(self, remote_target):
        key = self.bucket.get_key(remote_target)
        if key is None:
            return False
        return True

    def extract(self, archive_name):         
        tar = tarfile.open(archive_name)
        tar.extractall()
        tar.close()
            
    def compress(self, archive_name, files, compression='w:bz2'):
        # assert compression[0] == 'w', "we are writing"
        tar = tarfile.open(archive_name, compression)
        for k,v  in files.iteritems():
            tar.add(k, arcname=v)
        tar.close()
        

class Instance(object):
    """An AWS EC2 Instance"""
    
    def __init__(self, configuration):
        self._config = configuration
        self._state = None
        
        self._user_data = pickle.dumps(self._config)
        
        self._conn = boto.connect_ec2(aws_access_key_id=self._config.access_key,
            aws_secret_access_key=self._config.secret_key)
    
    def run(self):
        if self._config.spot is True:
            self._spot()
        else:
            self._on_demand()
        assert hasattr(self, '_reservation'), "Reservation not created."
        self._instance = self._reservation.instances[0]
        self.update()
    
    def _spot(self):
        assert hasattr (self._config, 'price'), \
            "Must set maximum spot price Configuration.spot"
        self._instances = self.conn.request_spot_instances(self._config.spot_price,
                self._config.instance_image,
                count=1,
                key_name=self._config.key_name,
                user_data=self._user_data,
                instance_type=self._config.instance_type)
    
    def _on_demand(self):
        self._reservation = self._conn.run_instances(self._config.instance_image,
                max_count=1,
                key_name=self._config.key_name,
                user_data=self._user_data,
                instance_type=self._config.instance_type)
    
    def terminate(self):
        self._instance.terminate()
    
    def stop(self):
        self._instance.stop()
    
    def update(self):
        self._state = self._instance.update()
    
    @property
    def state(self):
        if self._state is None:
            return "not-created"
        self.update()
        return self._state
            
    @property
    def instance_id(self):
        if self._state is None:
            return None
        return self._instance.id
        
    @property
    def dns_name(self):
        return self._instance.dns_name
        

class Cluster(object):
    """A group of identical AWS EC2 Instances"""
    
    def __init__(self, configuration):        
        self._config = configuration
        self._instances = []
        
        store = Store(self._config)
        store.compress(self._config.job_archive, self._config.file_manifest)
        store.push(self._config.job_archive, self._config.job_archive, overwrite=True)
        
        for n in range(self._config.instance_count):
            i = Instance(self._config)
            self._instances.append(i)
            
    def __len__(self):
        return len(self_instances)
            
    def start(self):
        [i.run() for i in self._instances]

    def stop(self):
        [i.stop() for i in self._instances]
    
    def terminate(self):
        [i.terminate() for i in self._instances]
      
    @property
    def instances(self):
        return self._instances
        
    @property
    def instance_ids(self):
        return [i.instance_id for i in self._instances]

    @property
    def dns_names(self):
        return [i.dns_name for i in self._instances]
        
        
class JobMaster(object):
    """The job on an actual Instance"""
    
    def __init__(self, in_cloud=True, user_data=None):
        self._in_cloud = in_cloud 
        self._id = 'local'
        
        if in_cloud is True:
            try:
                self._id = urllib.urlopen("http://169.254.169.254/latest/meta-data/instance-id").read()
            except IOError: # Probably not actually in the cloud
                self._in_cloud = False
    
        # TODO: Need some error checking here to ensure we end up with a config
        if self._in_cloud is True:        
            self._config = pickle.load(file("/var/lib/cloud/data/user-data.txt"))
            store = Store(self._config)
            store.pull(self._config.job_archive, self._config.job_archive)
            store.extract(self._config.job_archive)
        else:
            self._config = user_data
            
        self._config.instance_id = self._id

    def run(self):       
        # Hackish?
        job = __import__(self._config.job_file.split('.')[0])
        
        pool = multiprocessing.Pool(processes=self._config.pool_size)
        output = pool.imap_unordered(job.run,
            itertools.repeat(self._config.job_config, self._config.pool_size))
        pool.close()
        pool.join()
                
        # After all jobs in the pool have finished, combine process output
        job.combine(self._config, output)
            

