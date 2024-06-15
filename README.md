# Welcome to Rungpu!

## This is short document that helps you kickstart your finetuning Journey with Rungpu.

We provide you with the client side python module - rungpu.py
This module contains all the classes you would want to invoke to do the following tasks: 
- Create a Model and Quantize it.
- Create a Dataset and Store it. (from the cloud)
- Fine-tune a model on a dataset and save the finetuned tensors in the backend for later use.


## First Steps
Step 0: Clone this project onto your device.
Step 1. import the required classes from the rungpu module into your blank script. You would have to import from the whole path to the module like so:

``` from <path-to-library>/rungpu import Model```


### Create a Dataset
  To create a dataset, one must have a text file that's pre-formatted sitting in a cloud server. Given the credentials, rungpu pulls the file into the server and stores it under a specific dataset_id
  The config for which looks like following: 

    -- config.json
    ```
{
  "type": "azureblob",
  "env_auth": "false",
  "account": "rungpudev",
  "key": "<key>",
  "sas_url": "<sas_url>",
  "src_file": "datasets/test.txt",
  "dest_file": "data.txt"
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
  "root_path": "./models",
  "quant": 8,
  "num_steps": 300,
  "base_path": "microsoft/phi-2",
  "strategy": "lora",
  "checkpoint_steps": 100,
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
        finetune = Finetune(config)
```

Step 3: Make the start_finetune() call to trigger the finetune job in the backend

```
  finetune.start_finetune()
```
This call starts a finetune job. You get an instant response message from the server describing your job, the config and when your finetune job has started. 





