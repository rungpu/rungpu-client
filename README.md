# Welcome to Rungpu!

## This is short document that helps you kickstart your finetuning Journey with Rungpu.

We provide you with the client side python module - rungpu.py
This module contains all the classes you would want to invoke to do the following tasks: 
- Create a Model and Quantize it.
- Create a Dataset and Store it. (from the cloud)
- Fine-tune a model on a dataset and save the finetuned tensors in the backend for later use.

Clone this repository on your device. 
## First Steps

Step 0: Create a client object using the Client Class 

Step 1. import the required classes from the rungpu module into your blank script. You would have to import from the whole path to the module like so:

``` from <path-to-library>/rungpu import Model```


### Create a Dataset
  To create a dataset, one must have a text file that's pre-formatted sitting in a cloud server. Given the credentials, rungpu pulls the file into the server and stores it under a specific dataset_id
  The config for which looks like following: 

    -- config.json
    ```
{
    "config": {
        "type": "s3",
        "provider": "AWS",
        "env_auth": "false",
        "access_key_id": <Your AWS ACCESS KEY ID>,
        "secret_access_key": <Your AWS Secret ACCESS KEY>,
        "region": "us-east-1",
        "src_file": "/rungpu-dev/test.txt",
    }
}
     
```

  This config needs to be stored in a file.or directly entered as a json object variable.The file path needs to be entered as a parameter to a Dataset object like the following script. 

  ```
    from rungpu import Dataset

    dataset = Dataset(client=client, config=dataset_config)

  ```

This object stores in essence a reference to your dataset. which can be pulled from the cloud using the create_dataset() command. 

```
    dataset_response = dataset.create_dataset()
```

the `dataset_response` variable consist of the unique dataset id that is generated when the dataset is created, along with essential info about when it was created, where it is stored and whether or not there was an error while creating said dataset. 


### Start Finetuning

If you simply want to run a finetuning job on a given qunatized model, you do the following : -

#### Step 1:  Build Your config

Now this is where you have to get specific. Building config is basically creating a json object in the following shape. This json object as a whole would exist inside a json file on your machine. This json config is the fingerprint to a specific finetuning job. 

```
{
    "base_model": "mistralai/Mistral-7B-Instruct-v0.2",
    "quant": 8,
    "num_steps": 100,
    "strategy": "lora",
    "checkpoint_steps": 10,
    "training_size": 1000,
    "model_max_length": 4096,
    "prompt_max_length": 512,
    "peft_config": {
        "lora": {
            "r": 16,
            "alpha": 16,
            "target_modules": [
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
                "lm_head"
            ],
            "bias": "none",
            "lora_dropout": 0.05
        }
    }
}
```

This json would essentially encapsulate the nitty gritty details of your Finetuning task. here's a breakdown of the paramters mentioned: 

`root_path` : Where you would want your models to be stored
`quant` :  How many bits you would want your model to be quantized to
`num_steps` : Number of steps you want fine-tune your model in. 
`base_path` : The base path of the huggingface model youwill be using. 
`dataset_id` : Dataset ID - Every dataset you create in rungpu will have a unique dataset_id. This id will be stored in a datasets folder in our backend. You can simply identify a dataset for a specific fine-tune job using this id. 
`strategy` : The fine-tune strategy you would want to use to fine-tune your model. (Currently We accept Peft-LoRA) 
`checkpoint_steps`: Breakpoints at every x steps to checkpoint your model fine-tuning. 
`peft_config` : this is a sub-object that has Peft-LoRA specific Arguments. 
      `r`: the rank of the update matrices, expressed in int. Lower rank results in smaller update matrices with fewer trainable parameters.
      `alpha`:  LoRA scaling factor.
      `target_modules`:  The modules (for example, attention blocks) to apply the LoRA update matrices.
      `bias` : Specifies if the bias parameters should be trained. Can be 'none', 'all' or 'lora_only'.
      `lora_dropout`: Refers to the dropout rate applied to the fine-tuning process. 

#### Step 2: Create your finetune object

```
	from rungpu import Finetune
        finetune = Finetune(config=config, config_path = config_path)
```

You can either provide the config from a .json file by entering the filepath in the config_path argument or provide the raw json config in the config argument.

Step 3: Make the start_finetune() call to trigger the finetune job in the backend

```
  run_id = finetune.run_finetune()
```
This call starts a finetune job. You get an instant response message from the server describing your job, the config and when your finetune job has started. 


Step 4: Check the status of your job. 

Create a status object, using the Status() class, and pass the run_id , which was created when your finetuning job was kicked off. 

```
status = Status(run_id)

status = status.get_status()

```

this command returns an object like so: 

```
{'RunID': 'mistralai-Mistral-7B-Instruct-v0.2-8-bit-d52939f8-2b12-11ef-a04b-b8ca3a5c98fc-rungpu_dataset_efe1cfa4-8575-46c4-b11c-e3ba0a91d5c9',
 'time_elapsed': '43.20548573333333',
 'RunStatus': {'command': 'Finetune',
  'status': 'RUNNING',
  'phase': 'MODEL_EXPORT',
  'client_id': 'arun_prasad',
  'model_id': '<mistralai-Mistral-unique_model_id>',
  'base_model': 'mistralai/Mistral-7B-Instruct-v0.2',
  'dataset_id': '<rungpu_dataset_id>',
  'run_start': '2024-06-15 22:28:55.848158',
  'run_end': 'null',
  'export_start': '2024-06-15 22:44:36.149066',
  'export_end': 'null',
  'quantization': 8,
  'strategy': 'lora',
  'checkpoint_steps': 10,
  'training_steps': 100,
  'training_split': 1000,
  'peft_config': {'lora': {'r': 16,
    'alpha': 16,
    'target_modules': ['q_proj',
     'k_proj',
     'v_proj',
     'o_proj',
     'gate_proj',
     'up_proj',
     'down_proj',
     'lm_head'],
    'bias': 'none',
    'lora_dropout': 0.05}},
  'run_history': [{'loss': 1.7817,
    'grad_norm': 3.3305726051330566,
    'learning_rate': 0.0,
    'epoch': 0.46029919447640966,
    'step': 100},
   {'train_runtime': 835.0842,
    'train_samples_per_second': 0.958,
    'train_steps_per_second': 0.12,
    'total_flos': 1.75796669251584e+16,
    'train_loss': 1.7816670227050782,
    'epoch': 0.46029919447640966,
    'step': 100}]}}

```


This status is refreshed as the job progresses. You can run this cell over and over again to check how long it takes to run each training phase of the job.


