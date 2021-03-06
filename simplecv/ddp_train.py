import argparse
import torch
import torch.nn as nn
import torch.distributed as dist
from simplecv.module.model_builder import make_model
from simplecv.data.data_loader import make_dataloader
from simplecv.opt.optimizer import make_optimizer
from simplecv.opt.learning_rate import make_learningrate
from simplecv.util import config
from simplecv.core import trainer
from simplecv.util import param_util

parser = argparse.ArgumentParser()
parser.add_argument("--local_rank", type=int)
parser.add_argument('--config_path', default=None, type=str,
                    help='path to config file')
parser.add_argument('--model_dir', default=None, type=str,
                    help='path to model directory')
parser.add_argument('--cpu', action='store_true', default=False, help='use cpu')


def run(local_rank, config_path, model_dir, cpu_mode=False, after_construct_launcher_callbacks=None):
    # 0. config
    cfg = config.import_config(config_path)

    # 1. model
    model = make_model(cfg['model'])

    if not cpu_mode:
        if torch.cuda.is_available():
            torch.cuda.set_device(local_rank)
            dist.init_process_group(
                backend="nccl", init_method="env://"
            )
        model.to(torch.device('cuda'))
        if dist.is_available():
            model = nn.parallel.DistributedDataParallel(
                model, device_ids=[local_rank], output_device=local_rank,
            )

    # 2. data
    traindata_loader = make_dataloader(cfg['data']['train'])
    testdata_loader = make_dataloader(cfg['data']['test']) if 'test' in cfg['data'] else None

    # 3. optimizer
    lr_schedule = make_learningrate(cfg['learning_rate'])
    cfg['optimizer']['params']['lr'] = lr_schedule.base_lr
    optimizer = make_optimizer(cfg['optimizer'], params=model.parameters())
    tl = trainer.Launcher(
        model_dir=model_dir,
        model=model,
        optimizer=optimizer,
        lr_schedule=lr_schedule)

    if after_construct_launcher_callbacks is not None:
        for f in after_construct_launcher_callbacks:
            f(tl)

    tl.train_by_config(traindata_loader, config=cfg['train'], test_data_loader=testdata_loader)


if __name__ == '__main__':
    args = parser.parse_args()
    assert args.config_path is not None, 'The config file is needed.'
    assert args.model_dir is not None, 'The model dir is needed.'
    run(local_rank=args.local_rank,
        config_path=args.config_path,
        model_dir=args.model_dir,
        cpu_mode=args.cpu)
