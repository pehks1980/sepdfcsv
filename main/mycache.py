import pymemcache as mc


# Create a memcached client object
def create_client():
    client = mc.Client(('localhost', 11211))
    return client


def update_progress(mc, thread_id, progress):
    exporting_thread = mc.get(str(thread_id))
    if exporting_thread:
        exporting_thread = eval(exporting_thread.decode())
        exporting_thread['progress'] = progress
        mc.set(str(thread_id), exporting_thread)
