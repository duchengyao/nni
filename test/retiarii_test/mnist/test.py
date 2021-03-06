import random

import nni.retiarii.nn.pytorch as nn
import torch.nn.functional as F
from nni.retiarii.experiment import RetiariiExeConfig, RetiariiExperiment
from nni.retiarii.strategies import RandomStrategy
from nni.retiarii.trainer import PyTorchImageClassificationTrainer


class Net(nn.Module):
    def __init__(self, hidden_size):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.LayerChoice([
            nn.Linear(4*4*50, hidden_size),
            nn.Linear(4*4*50, hidden_size, bias=False)
        ])
        self.fc2 = nn.Linear(hidden_size, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*50)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


if __name__ == '__main__':
    base_model = Net(128)
    trainer = PyTorchImageClassificationTrainer(base_model, dataset_cls="MNIST",
                                                dataset_kwargs={"root": "data/mnist", "download": True},
                                                dataloader_kwargs={"batch_size": 32},
                                                optimizer_kwargs={"lr": 1e-3},
                                                trainer_kwargs={"max_epochs": 1})

    simple_startegy = RandomStrategy()
    
    # 1. ------------------------------------
    
    trainer.fit(NET) 
    # see https://github.com/microsoft/nni/blame/master/docs/en_US/NAS/retiarii/Tutorial.rst#L177
    # TypeError: __init__() missing 1 required positional argument: 'hidden_size'
    
    # 2. ------------------------------------
    
    trainer.fit(base_model)
    # RuntimeError: mat1 and mat2 shapes cannot be multiplied (100x800 and 128x10)
    
    # 3. ------------------------------------
    
    base_model = Net(800)
    trainer.fit(base_model)
    # Is able to run, but LayerChoice is useless. 
    # I just want to run this script in only command line mode.

    
    
    # ==================================================================================================
    # exp = RetiariiExperiment(base_model, trainer, [], simple_startegy)
    # 
    # exp_config = RetiariiExeConfig('local')
    # exp_config.experiment_name = 'mnist_search'
    # exp_config.trial_concurrency = 2
    # exp_config.max_trial_number = 10
    # exp_config.training_service.use_active_gpu = False
    # 
    # exp.run(exp_config, 8081 + random.randint(0, 100))
