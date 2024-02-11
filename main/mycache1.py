import requests
import json



class KeyValueStore:
    _instance = None
    # each call class will give the same class ref once created SINGELTON
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # If the instance doesn't exist, create it
            cls._instance = super().__new__(cls)
            # init with param
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self, url):
        self.api_url = url

    def set(self, key, value, expiry="-1"):
        url = f"{self.api_url}/put/"
        data = {"key": key, "value": value, "expiry": expiry}
        response = self._send_post_request(url, data)
        return response

    def get(self, key):
        url = f"{self.api_url}/get/"
        data = {"key": key}
        response = self._send_post_request(url, data)
        return response

    def _send_post_request(self, url, data):
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending POST request: {e}")
            return None


def create_client(CACHE_URL="http://127.0.0.1:8000"):
    client = KeyValueStore(CACHE_URL)
    return client


# Example Usage:
key_value_store = KeyValueStore("http://127.0.0.1:8000")

# Set example
set_response = key_value_store.set("bla", "value1", "60")
print(f"Set Response: {set_response}")

# Get example
get_response = key_value_store.get("bla")
print(f"Get Response: {get_response}")

get_response = key_value_store.get("bla1")
print(f"Get Response: {get_response}")


# Update current progress of exporting process
# (get and manual set value 0-100 from cache, key is 'thread_id')
# mode showd current mode file
def update_progress(mc, thread_id, progress, mode=''):
    #    exporting_thread = mc.get(str(thread_id))
    #    data_dict = json.loads(exporting_thread)
    #    if data_dict['value'] == "":
    #    exporting_thread = eval(exporting_thread.decode())

    exporting_thread_new = {'progress': progress, 'mode': mode}
    json_string = json.dumps(exporting_thread_new)
    mc.set(str(thread_id), json_string)
