"""Thin nn.Module around the vendored BEATs encoder."""

import torch
import torch.nn as nn

from .beats.BEATs import BEATs, BEATsConfig


class BEATsWrapper(nn.Module):
    def __init__(self):
        super().__init__()
        self.beats = BEATs(BEATsConfig())

    def mel_forward(self, x):
        with torch.autocast(device_type="cuda", enabled=False):
            mel = self.beats.preprocess(x)
        return mel.unsqueeze(1).transpose(2, 3)

    def forward(self, x):
        x = x.transpose(2, 3)
        return self.beats.extract_features(x, do_preprocess=False)[0]
