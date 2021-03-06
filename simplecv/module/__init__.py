from simplecv import registry
import torch.nn as nn

registry.OP.register('batchnorm', nn.BatchNorm2d)
registry.OP.register('groupnorm', nn.GroupNorm)
# basic component
from simplecv.module.aspp import AtrousSpatialPyramidPool
from simplecv.module.sep_conv import SeparableConv2D
from simplecv.module.gap import GlobalAvgPool2D
from simplecv.module.se_block import SEBlock

# encoder
from simplecv.module.resnet import ResNetEncoder


# loss
from simplecv.module import loss

