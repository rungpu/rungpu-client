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


class TrainStatus:
    def __init__(self,client,train_id):
        self.client=client
        self.train_id = train_id
        self.train_id = train_id
        self.base_model = None
        self.quantization = None

    def get_status(self):
        
        url = f"{base_url}/trainstatus"
        status_config = {"train_id":self.train_id}
        url = f"{base_url}/trainstatus"
        status_config = {"train_id":self.train_id}
        status_config['client_id'] = self.client.client_id
        status_config['client_secret'] = self.client.client_secret
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
        data = json.loads(response.text)
        
        df = pd.DataFrame(data['jobs'])
        return data
    

    def progress(self,offset=0,training=0):
        url = f"{base_url}/progress"
        training = training
        status = self.get_status()
        self.base_model = status['train_status']['base_model'].replace('/','-')
        self.quantization = status['train_status']['quantization']
        self.base_model = status['train_status']['base_model'].replace('/','-')
        self.quantization = status['train_status']['quantization']
        while True:
            data = {"train_id":self.train_id, "offset": offset,"training":training,"specs":{"base_model":self.base_model, "quantization": self.quantization}}
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
                
       
    

class EvalStatus:

    def __init__(self,client,model_id,dataset_id):
        self.client = client
        self.model_id = model_id
        self.dataset_id = dataset_id


    def get_eval_status(self):
        url = f"{base_url}/evalstatus"
        status_config = {"model_id": f"{self.model_id}", "dataset_id":f"{self.dataset_id}"}
        status_config["client_id"] = self.client.client_id
        status_config["client_secret"] = self.client.client_secret
        response = requests.get(url, json=status_config)
        if response.status_code == 200:
            data = json.loads(response.text)
        else:
            data = {"message":"There was a problem retrieving the status.Please try again"}

        return data
    
    def get_responses(self, line=0):
        url = f"{base_url}/evalstream"

        status_config = {"model_id": f"{self.model_id}", "dataset_id":f"{self.dataset_id}"}
        status_config["client_id"] = self.client.client_id
        status_config["client_secret"] = self.client.client_secret

        response = requests.get(url,json=status_config)
        
        if response.status_code ==200:
            return response.text
        else:
            return "There was a problem Streaming the response."
    
    def eval_progress(self,offset=0,flag=0):
        url = f"{base_url}/eval_progress"
        flag = flag
        while True:
            data = {"model_id":self.model_id,"dataset_id": self.dataset_id, "offset": offset,"flag":flag}
            data["client_id"] = self.client.client_id
            data["client_secret"] = self.client.client_secret
            response = requests.get(url,json=data)
            obj = json.loads(response.text)
            if(obj['log']):
                message = obj["text"]
                size = obj['size']
                offset = obj['offset'] 
                flag = obj['training']
                sleep_time = obj['sleep']
                sleep(sleep_time)
                msg_split = message.split('\n')
                message = msg_split[0]
                offset-= len(' '.join(msg_split[1:]))
                if ("**END**" in message):
                    print("EVAL COMPLETED")
                    break
                if message == '':
                    print('',end="")
                else:
                    print(message)
            else:
                print("Your Job is still in the queue")
                sleep(30)



       
    
 

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

    def __init__(self,client,mode='train', config = None, config_path= None):
        self.client = client
        self.mode = mode
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
        dataset_json["mode"] = self.mode
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
        model_config['client_id'] = self.client.client_id
        model_config['client_secret'] = self.client.client_secret 
        response = requests.get(url,json=model_config)
        return response.json()
        

    
class Eval:
    def __init__(self,client,model_id, dataset_id):
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.client = client
   
    def run_inference(self):
        url = f"{base_url}/eval"
        model_config = {"model_id": self.model_id, "dataset_id": self.dataset_id}
        model_config['client_id'] = self.client.client_id
        model_config['client_secret'] = self.client.client_secret
        print(f"Model Configuration : \n{model_config}")
        response = requests.post(url,json=model_config)
        return response.json()



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