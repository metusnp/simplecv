import torch.nn as nn


class CVModule(nn.Module):
    def __init__(self, config):
        super(CVModule, self).__init__()
        self._cfg = dict(
            type='',
            params=dict()
        )
        self.set_defalut_config()
        self._update_config(config)

    def forward(self, *input):
        raise NotImplementedError

    def set_defalut_config(self):
        raise NotImplementedError

    def _update_config(self, new_config):
        self._cfg.update(new_config)

    @property
    def config(self):
        return self._cfg

    def __repr__(self):
        s = '[config]\n'
        for k, v in self.config.items():
            s += '{name} = {value}\n'.format(name=k, value=v)
        s += '[------]'
        return s


class Loss(CVModule):
    def __init__(self, config):
        super(Loss, self).__init__(config)

    def forward(self, *input):
        raise NotImplementedError


class LearningRateBase(object):
    def __init__(self):
        pass

    def step(self, global_step, optimizer):
        raise NotImplementedError