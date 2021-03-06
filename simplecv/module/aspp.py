import torch
import torch.nn as nn
import torch.nn.functional as F
from simplecv import registry
from simplecv.module.sep_conv import SeparableConv2D
from simplecv.module.gap import GlobalAvgPool2D
from simplecv.util import param_util


@registry.OP.register('aspp')
class AtrousSpatialPyramidPool(nn.Module):
    def __init__(self,
                 in_channel,
                 aspp_dim=256,
                 atrous_rates=(6, 12, 18),
                 add_image_level=True,
                 use_bias=True,
                 use_batchnorm=False,
                 batchnorm_trainable=False,
                 norm_type='batchnorm'):
        super(AtrousSpatialPyramidPool, self).__init__()
        norm_fn = registry.OP[norm_type]

        self.add_image_level = add_image_level
        self.rate_list = atrous_rates
        self.add_image_level = add_image_level
        self.use_batchnorm = use_batchnorm
        self.batchnorm_trainable = batchnorm_trainable
        self.aspp_dim = aspp_dim

        layers = [nn.Conv2d(in_channel, aspp_dim, kernel_size=1, bias=use_bias)]
        if use_batchnorm:
            layers.append(norm_fn(aspp_dim))
        layers.append(nn.ReLU(inplace=True))
        self.conv1x1 = nn.Sequential(*layers)

        self.aspp_convs = nn.ModuleList()
        for rate in atrous_rates:
            self.aspp_convs.append(
                nn.Sequential(
                    SeparableConv2D(in_channel, aspp_dim, kernel_size=3, stride=1, padding=rate, dilation=rate,
                                    bias=use_bias, use_batchnorm=use_batchnorm, norm_fn=norm_fn),
                    nn.ReLU(inplace=True)
                )
            )

        if add_image_level:
            self.image_pool = nn.Sequential(
                GlobalAvgPool2D(),
                nn.Conv2d(in_channel, aspp_dim, kernel_size=1, bias=use_bias),
                nn.ReLU(inplace=True)
            )
        merge_inchannel = 1 + len(atrous_rates) + int(add_image_level)
        # projection
        layers = [nn.Conv2d(merge_inchannel * aspp_dim, aspp_dim, kernel_size=1, bias=use_bias)]
        if use_batchnorm:
            layers.append(norm_fn(aspp_dim))
        layers.append(nn.ReLU(inplace=True))
        self.merge_conv = nn.Sequential(*layers)
        self.dropout = nn.Dropout(p=0.1)

        if self.use_batchnorm and not self.batchnorm_trainable:
            param_util.freeze_modules(self, nn.BatchNorm2d)
            for m in self.modules():
                if isinstance(m, nn.BatchNorm2d):
                    m.eval()

    def forward(self, x):
        # aspp feat
        c1 = self.conv1x1(x)

        aspp_feat_dict = {'conv1x1': c1}
        for aspp_conv_op in self.aspp_convs:
            aspp_feat = aspp_conv_op(x)
            aspp_feat_dict['artous_rate_{}'.format(aspp_conv_op[0].dilation)] = aspp_feat
        # image level feat
        if self.add_image_level:
            image_feature = self.image_pool(x)
            image_feature = F.interpolate(image_feature, size=(c1.size(2), c1.size(3)), mode='bilinear',
                                          align_corners=True)
            aspp_feat_dict['image_level'] = image_feature
        # merge op
        branch_logits = list(aspp_feat_dict.values())
        concat_logits = torch.cat(branch_logits, dim=1)
        concat_logits = self.merge_conv(concat_logits)

        concat_logits = self.dropout(concat_logits)

        return concat_logits
