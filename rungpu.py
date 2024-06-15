import requests
import json
import pandas as pd
import re
from time import sleep

base_url = "https://p2y2xn5ac6.execute-api.us-east-1.amazonaws.com"


class Client:
    def __init__(self,client_id,client_secret):
        self.client_id = client_id
        self.client_secret = client_secret


class Status:

    def __init__(self,run_id):
        self.run_id = run_id
        self.base_model = None
        self.quantization = None

    def get_status(self):

        url = f"{base_url}/runstatus"
        status_config = {"run_id":self.run_id}
        status_json = json.dumps(status_config)
        response = requests.get(url, json=status_config)
        data = json.loads(response.text)

        return data
    
    @staticmethod
    def get_jobs(client,type='json'):
        client_id = client.client_id
        url = f"{base_url}/viewruns"
        client_id = {"client_id": client_id}
        response = requests.get(url, json=client_id)
        print(response.status_code)
        data = json.loads(response.text)
        
        df = pd.DataFrame(data['jobs'])
        return data
    

    def progress(self,offset=0,training=0):
        url = f"{base_url}/progress"
        training = training
        status = self.get_status()
        self.base_model = status['RunStatus']['base_model'].replace('/','-')
        self.quantization = status['RunStatus']['quantization']
        while True:
            
            data = {"run_id":self.run_id, "offset": offset,"training":training,"logfile":f"{self.base_model}/{self.quantization}"}
            response = requests.get(url,json=data)
            obj = json.loads(response.text)
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
        

class Model:
    def __init__(self, config):
        self.base_model = config['base_path']
        self.quantify_bit = config['quant']

    def create_model(self):
        url = f"{base_url}/create-model"
        model_config = {'base_path':self.base_model, 'quant':self.quantify_bit}
        response = requests.post(url, json=model_config)
        return response.json()
    

class Dataset:

    def __init__(self,client, config = None, config_path= None):
        self.client = client
        if config is None and config_path is None:
            raise ValueError('You need to provide a valid json config, or the path to your valid json config file. ')
        elif config is None and config_path is not None:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        elif config_path is None and config is not None:
            self.config = config
        else:
            self.config = config
            self.config_path = config
        
    
    def create_dataset(self):
        # dataset_config_file = open(self.config_path, 'r')
        dataset_json = self.config
        dataset_json["client_id"] = self.client.client_id
        dataset_json["client_secret"] = self.client.client_secret
        url = f"{base_url}/create-dataset"
        response = requests.post(url, json=dataset_json)
        data = json.loads(response.text)
        return data


class Finetune:

    def __init__(self,client,dataset_id, config_path=None,config=None):
        self.client = client
        self.dataset_id = dataset_id
        if config is None and config_path is None:
            raise ValueError('You need to enter a json config or a path to a json file.')
        elif config is None and config_path is not None:
            with open(config_path,'r') as f:
                self.config = json.load(f)
        elif config_path is None and config is not None:
            self.config = config
        else:
            self.config = config 
            self.config_path = config_path
        self.base_model = self.config['base_model'].replace('/','-')
        self.quantization = self.config['quant']
        
        

    def run_finetune(self):
        finetune_config_json = self.config 
        finetune_config_json['dataset_id'] = str(self.dataset_id)
        finetune_config_json['client_id'] = str(self.client.client_id)
        finetune_config_json['client_secret'] = str(self.client.client_secret)

        url = f"{base_url}/finetune"
        response = requests.post(url, json=finetune_config_json)
        data = json.loads(response.text)
        return data
    
    def get_model(self,model_id):
        url = f"{base_url}/getmodel"
        model_config = {'model_id':model_id}
        response = requests.get(url,json=model_config)
        return response.json()
        

    

    


