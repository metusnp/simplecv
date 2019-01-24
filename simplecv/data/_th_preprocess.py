import torch
import torch.nn.functional as F


def _th_resize_to_range(image, min_size, max_size):
    h = image.size(0)
    w = image.size(1)
    c = image.size(2)
    im_size_min = min(h, w)
    im_size_max = max(h, w)

    im_scale = min(min_size / im_size_min, max_size / im_size_max)

    image = F.interpolate(image.permute(2, 0, 1).view(1, c, h, w), scale_factor=im_scale, mode='bilinear')
    return image, im_scale


def _th_mean_std_normalize(image, mean=(123.675, 116.28, 103.53), std=(58.395, 57.12, 57.375)):
    """ this version faster than torchvision.transforms.functional.normalize


    Args:
        image: 3-D or 4-D array of shape [batch (optional) , height, width, channel]
        mean:  a list or tuple or ndarray
        std: a list or tuple or ndarray

    Returns:

    """
    shape = [1] * image.dim()
    shape[-1] = -1
    mean = torch.tensor(mean, requires_grad=False).reshape(*shape)
    std = torch.tensor(std, requires_grad=False).reshape(*shape)

    return image.sub(mean).div(std)


def _th_mean_std_normalize_(image, mean=(123.675, 116.28, 103.53), std=(58.395, 57.12, 57.375)):
    """ this version faster than torchvision.transforms.functional.normalize


    Args:
        image: 3-D or 4-D array of shape [batch (optional) , height, width, channel]
        mean:  a list or tuple or ndarray
        std: a list or tuple or ndarray

    Returns:

    """
    shape = [1] * image.dim()
    shape[-1] = -1
    mean = torch.tensor(mean, requires_grad=False).reshape(*shape)
    std = torch.tensor(std, requires_grad=False).reshape(*shape)

    return image.sub_(mean).div_(std)
