import requests
import json
import pandas as pd
import re
from time import sleep


base_url = "https://p2y2xn5ac6.execute-api.us-east-1.amazonaws.com"

class Client:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret


class Model:
    def __init__(self,client,config):
        self.client = client
        self.config = config
    
    def train_model(self):
        img_flag = self.check_data(self.config['dataset_id'])
        
        if(img_flag['dataset_status']['status'] and img_flag['dataset_status']['status'] == 'COMPLETED'):
            url = f"{base_url}/vision"
            config = self.config
            config["client_id"] = str(self.client.client_id)
            config["client_secret"] = str(self.client.client_secret)
            response = requests.post(url, json=self.config)
            data = json.loads(response.text)
            return data
        else:
            return {"message": "Your dataset hasn't been created yet please try in some time."}

    def check_data(self,dataset_id):
        url = f"{base_url}/visiondatastatus"
        dataset_config = self.config
        dataset_config['dataset_id'] = dataset_id
        dataset_config['client_id'] = self.client.client_id
        dataset_config['client_secret'] = self.client.client_secret
        status_json = json.dumps(dataset_config)
        response = requests.get(url, json=dataset_config)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data
        else:
            return {"message": "Something Went wrong"}
    



class VisionDataset:
    def __init__(self,client,config):
        self.client = client
        self.config = config

    def create_dataset(self):
        url = f"{base_url}/visiondataset"
        dataset_config = self.config
        dataset_config['client_id'] = self.client.client_id
        dataset_config['client_secret'] = self.client.client_secret
        status_json = json.dumps(dataset_config)
        response = requests.post(url, json=dataset_config)
        data = json.loads(response.text)
        return data
    
    def check_data(self,dataset_id):
        url = f"{base_url}/visiondatastatus"
        dataset_config = self.config
        dataset_config['dataset_id'] = dataset_id
        dataset_config['client_id'] = self.client.client_id
        dataset_config['client_secret'] = self.client.client_secret
        status_json = json.dumps(dataset_config)
        response = requests.get(url, json=dataset_config)
        data = json.loads(response.text)
        return data
    
    


class VisionStatus:
    def __init__(self,client,model_id):
        self.client = client
        self.model_id = model_id

    def get_status(self):
        
        url = f"{base_url}/visionstatus"
        status_config = {"model_id":self.model_id}
        status_config['client_id'] = self.client.client_id
        status_config['client_secret'] = self.client.client_secret
        status_json = json.dumps(status_config)
        response = requests.get(url, json=status_config)
        data = json.loads(response.text)

        return data
    
    def get_download_links(self):
        url = f"{base_url}/downloadvisionlink"
        status_config = {"model_id":self.model_id}
        status_config['client_id'] = self.client.client_id
        status_config['client_secret'] = self.client.client_secret
        status_json = json.dumps(status_config)
        response = requests.get(url, json=status_config)
        data = json.loads(response.text)

        return data
    

    
    
    def progress(self,offset=0,training=0):
        url = f"{base_url}/progress"
        training = training
        status = self.get_status()
        self.base_model = status['train_status']['base_model'].replace('/','-')
        self.quantization = status['train_status']['quantization']
        while True:
            data = {"train_id":self.train_id, "offset": offset,"training":training,"logfile":f"{self.base_model}/{self.quantization}"}
            data["client_id"] = self.client.client_id
            data["client_secret"] = self.client.client_secret
            response = requests.get(url,json=data)
            obj = json.loads(response.text)
            if(obj['log']):
                message = obj["text"]
                size = obj['size']
                offset = obj['offset'] 
                training = obj['training']
                sleep_time = obj['sleep']
                sleep(sleep_time)
                msg_split = message.split('\n')
                message = msg_split[0]
                offset-= len(' '.join(msg_split[1:]))
                if ("Training completed." in message):
                    print("Training Completed.")
                    break
                if message == '':
                    print('',end="")
                else:
                    print(message)
            else:
                print("Your Job is still in the queue")
                print("will retry in 30 seconds...")
                sleep(30)
                



__copyright__ = """
Copyright 2024. AI WHISPR PTY LTD

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, co, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:  The below
copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""