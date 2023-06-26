import pymemcache as mc


# Create a memcached client object
# to connect to cache
def create_client():
    client = mc.Client(('localhost', 11211))
    return client


# Update current progress of exporting process
# (get and manual set value 0-100 from cache, key is 'thread_id')
# mode showd current mode file
def update_progress(mc, thread_id, progress, mode=''):
    exporting_thread = mc.get(str(thread_id))
    if exporting_thread:
        exporting_thread = eval(exporting_thread.decode())
        exporting_thread['progress'] = progress
        exporting_thread['mode'] = mode
        mc.set(str(thread_id), exporting_thread)
