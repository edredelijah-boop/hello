"""Frame-level SED head on top of BEATs.

Architecture and the ``BEATs_strong_*`` checkpoints are from Schmid et al.,
"Effective Pre-Training of Audio Transformers for Sound Event Detection",
ICASSP 2025 (https://github.com/fschmid56/PretrainedSED). See docs/MODELS.md.
"""

import os

import torch
import torch.nn as nn

from .. import constants

N_CLASSES = constants.N_AUDIO_CLASSES
SEQ_LEN = 250          # output frames per 10 s chunk -> 40 ms resolution
EMBED_DIM = 768        # BEATs embedding width


class BEATsSED(nn.Module):
    """BEATs transformer + linear head.

    Input:  mel of one 10 s chunk.
    Output: (batch, 447, 250) frame-level logits.
    """

    def __init__(self, beats_wrapper, checkpoint_path):
        super().__init__()
        self.model = beats_wrapper
        self.strong_head = nn.Linear(EMBED_DIM, N_CLASSES)
        self.weak_head = nn.Linear(EMBED_DIM, N_CLASSES)   # unused; exists in checkpoint
        self._load_checkpoint(checkpoint_path)

    def _load_checkpoint(self, checkpoint_path):
        if not checkpoint_path or not os.path.exists(checkpoint_path):
            raise FileNotFoundError(
                f"BEATs SED checkpoint not found: {checkpoint_path!r}\n"
                f"Download BEATs_strong_1.pt from "
                f"https://github.com/fschmid56/PretrainedSED/releases and pass it "
                f"with --checkpoint or ${constants.ENV_BEATS_CHECKPOINT}."
            )
        sd = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        # remap keys: 'model.model.*' (upstream naming) -> 'model.beats.*' (ours)
        sd = {("model.beats." + k[len("model.model."):] if k.startswith("model.model") else k): v
              for k, v in sd.items()}
        missing, unexpected = self.load_state_dict(sd, strict=True)
        assert not missing and not unexpected

    def mel_forward(self, x):
        return self.model.mel_forward(x)

    def forward(self, x):
        x = self.model(x)                      # (B, ~496, 768) for a 10 s chunk
        if x.size(-2) != SEQ_LEN:              # pool ~496 -> 250 (40 ms grid)
            x = torch.nn.functional.adaptive_avg_pool1d(
                x.transpose(1, 2), SEQ_LEN).transpose(1, 2)
        return self.strong_head(x).transpose(1, 2)   # (B, 447, 250) logits
