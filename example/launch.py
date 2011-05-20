from manysim import Configuration, Cluster, JobMaster


job_config = {
    'job_id' : 'test',
    'value' : 100,
}

config_params = {
    'instance_type' : "t1.micro",
    'instance_image' : "ami-xxx",
    'access_key' : "ABC",
    'secret_key' : "123",
    'key_name' : "foo",
    'instance_count' : 1,
    'pool_size' : 10,
        
    'spot' : False,
    'spot_price' : 0.3,
        
    'bucket_name' : 'com.foo.bucket', 
    'job_archive' : 'job.tar.bz2',
    'file_manifest' : ['job.py'],
     
    'job_file' : 'job.py',
    'job_config' : job_config,
}

config = Configuration(**config_params)

# Local (with user_data override)
master = JobMaster(in_cloud=False, user_data=config)
master.run()

# Remote
#cloud = Cluster(config)
#cloud.start()    
#cloud.stop()
#cloud.terminate()
