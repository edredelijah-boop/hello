"""Audio-event stage: BEATs frame-level SED -> ``<video_id>.npy``.

Output is a ``(447, T)`` float16 probability matrix at 40 ms resolution
(25 steps/second). Row order follows ``audioset_classes.as_strong_train_classes``;
column ``t`` is source time ``t / 25`` seconds.
"""

import os

import numpy as np
import torch

from .. import constants, layout
from ..audioset_classes import as_strong_train_classes
from ..common.media import load_audio
from .head import BEATsSED
from .wrapper import BEATsWrapper

torch.backends.cudnn.enabled = False   # matches the scored configuration


def _resolve_checkpoint(checkpoint):
    return checkpoint or os.environ.get(constants.ENV_BEATS_CHECKPOINT)


def load_model(checkpoint, device):
    model = BEATsSED(BEATsWrapper(), _resolve_checkpoint(checkpoint))
    model.eval()
    model.to(device)
    return model


def pick_device(device="auto"):
    if device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(device)


def run_inference(waveform, model, device):
    """Chunk the waveform into 10 s pieces, run batched forward passes,
    and return a ``(447, T)`` float32 numpy array."""
    n_samples = len(waveform)
    n_chunks = n_samples // constants.CHUNK_SAMPLES + (n_samples % constants.CHUNK_SAMPLES != 0)

    padded = np.zeros(n_chunks * constants.CHUNK_SAMPLES, dtype=np.float32)
    padded[:n_samples] = waveform
    chunks = torch.from_numpy(padded).view(n_chunks, constants.CHUNK_SAMPLES)

    outputs = []
    with torch.no_grad():
        for start in range(0, n_chunks, constants.SED_BATCH_SIZE):
            batch = chunks[start:start + constants.SED_BATCH_SIZE].to(device)
            mel = model.mel_forward(batch)
            logits = model(mel)                          # (B, 447, 250)
            outputs.append(torch.sigmoid(logits).cpu())

    probs = torch.cat(outputs, dim=0)                    # (n_chunks, 447, 250)
    probs = probs.permute(1, 0, 2).reshape(len(as_strong_train_classes), -1)
    true_frames = int(np.ceil(n_samples / constants.SAMPLE_RATE / constants.FRAME_SECONDS))
    return probs[:, :true_frames].numpy()


def extract_audio_events(video_path, data_root, video_id=None,
                         checkpoint=None, device="auto", model=None,
                         progress=True):
    """Run SED on one video and save ``<data_root>/.../<video_id>.npy``.

    Pass a preloaded ``model`` to amortize checkpoint loading across a batch.
    Returns the output path.
    """
    video_id = video_id or os.path.splitext(os.path.basename(str(video_path)))[0]
    out_path = layout.npy_path(data_root, video_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dev = pick_device(device)
    if model is None:
        if progress:
            print(f"[audio] loading BEATs SED model on {dev}")
        model = load_model(checkpoint, dev)

    if progress:
        print(f"[audio] {video_id}: loading audio")
    waveform = load_audio(video_path)
    if progress:
        mins = len(waveform) / constants.SAMPLE_RATE / 60
        print(f"[audio] {video_id}: {mins:.1f} min -> running SED")

    probs = run_inference(waveform, model, dev)
    np.save(out_path, probs.astype(np.float16))
    if progress:
        print(f"[audio] {video_id}: {probs.shape} -> {out_path}")
    return out_path
