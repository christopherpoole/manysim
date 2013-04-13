#Introduction
What initially started out as an easy way of running GEANT4 simulations on AWS EC2, manysim is a simple technique for executing arbitary code on EC2 using Python and the [boto](http://code.google.com/p/boto/) Python module.
Jobs can be launched from the local user machine and executed on the EC2 with results returned to the user via S3. It is up to the user to configure an Amazon Machine Image with any packages or tools on it they require.


#manysim for GEANT4
Usage of manysim for running GEANT4 simulations is described in a pre-print publication, available [here](http://christopherpoole.github.io/Radiotherapy-Monte-Carlo-simulation-using-cloud-computing-technology/).
If you would like the cite the article, you may wish to use the following bibtex entry:
{{{
@article{poole2012cad,
    author={Poole, C.M. and Cornelius, I. and Trapp, J.V. and Langton, C.M.},
    journal={Australasian Physical & Engineering Sciences in Medicine},
    title={In-press. Radiotherapy Monte Carlo simulation using cloud computing technology},
    year={2012},
}
}}}

#Installation
Checkout a working copy for the source repository or use [http://pypi.python.org/pypi/manysim/ easy_install]:

    sudo easy_install manysim

Check out the wiki for some more specific information on [setting up] (http://code.google.com/p/manysim/wiki/CreateAMI) an Amazon Machine Image for use with manysim.

#Example Usage
Any job running on EC2 needs a configuration containing connection credentials and so on. Additionally, user configuration for the simulation can be specified in a dict:

    job_config = {
        'job_id' : 'test',
        'value' : 100,
    }

    config_params = {
        'access_key' : 'abc',
        'secret_key' : '123',
        
        # 160 Processors ~400 EC2 compute units
        'instance_type' : 'c1.xlarge',
        'instance_image' : 'ami_foo1',
        'instance_count' : 20,
        'pool_size' : 8,
            
        'spot' : True,
        'spot_price' : 0.3,
            
        'bucket_name' : 'com.name.bucket', 
        'job_archive' : 'job.tar.bz2',
        'file_manifest' : ['data.txt', 'job.py'],
         
        'job_file' : 'job.py',
        'job_config' : job_config,
    }

A job is described in a job file;  so long as the dependencies for the job are satisfied on the remote instance, the job can be pretty much anything you want. Two functions, `run` and `combine` are required, `run` is the code you want to execute and `combine` is an easy way of describing a custom handing of the output from the `n` workers on an instance. 

    import os
    import pickle

    from manysim import Store


    def run(job_config):
       """This is the simulation proper"""
      
       result = job_config['value'] * 2
       return (os.getpid(), result) 
     
     
    def combine(config, output):
        """Combine the worker results in some sensible way"""
        
        results = list(output)
            
        # The unique instance_id will be available automatically
        output_file = "output_%s" % config.instance_id
        pickle.dump(results, file(output_file, 'w'))

        # Persist on S3 if not local
        if config.instance_id != 'local':
            store = Store(config)
            store.push(output_file, config.bucket_name)

This job can be executed locally (for debugging) using a JobMaster, or a Cluster of instances can be launched for remote execution:

    from manysim import Configuration, Cluster, JobMaster

    config = Configuration(**config_params)

    # Local (with user_data override)
    master = JobMaster(in_cloud=False, user_data=config)
    master.run()
        
    # Remote
    cloud = Cluster(config)
    cloud.start()    
    #cloud.stop()
    cloud.terminate()

#Dependencies
A working installation of the following libraries or packages is required:
 * GEANT4 (only if you want to use GEANT4, `manysim` does not require this directly)
 * `boto` Python module

