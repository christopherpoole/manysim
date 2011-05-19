import os
import pickle
import random

from manysim import Store

def run(job_config):
    """This is the simulation proper"""

    result = job_config['value'] * random.random()
    return (os.getpid(), result) 
 
 
def combine(config, output):
    """Combine the worker results in some sensible way"""
    
    results = list(output)
    print results
           
    # The unique instance_id will be available automatically
    output_file = "output_%s" % config.instance_id
    pickle.dump(results, file(output_file, 'w'))

    # Persist on S3 if not local
    if config.instance_id != 'local':
        store = Store(config)
        store.push(output_file, output_file)
    

