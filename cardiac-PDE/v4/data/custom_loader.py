"""
data/custom_loader.py — Template for adding a new data source.

Copy this file, rename it, and implement the three abstract methods.
Then register the new class in data/base.py get_data_source().

Example:
    from data.base import get_data_source
    src = get_data_source("my_source", data_dir="./my_data")
    ic  = src.load_ic(sample_idx=0)
    snaps = src.load_snapshots(sample_idx=0)
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

import numpy as np

from data.base import DataSource, DatasetMetadata


class CustomLoader(DataSource):
    """
    Template for a new data source.

    Steps to implement:
    1. Set METADATA below to match your dataset.
    2. Implement load_ic() to return the initial condition arrays.
    3. Implement load_snapshots() to return the time-series snapshots.
    4. Register in data/base.py get_data_source().
    """

    # ── Edit these to match your dataset ────────────────────────────────────
    METADATA = DatasetMetadata(
        name="custom",
        n_vars=2,                       # number of state variables
        var_names=["u", "v"],           # variable names
        spatial_shape=(128, 128),       # (H, W) for 2D, (N,) for 1D
        n_time_steps=101,
        t_start=0.0,
        t_end=10.0,
        dt=0.1,
        dx=1.0 / 128,
        domain_size=1.0,
        params={},                      # model parameters dict
    )
    # ────────────────────────────────────────────────────────────────────────

    def __init__(self, data_dir: str = "./data/raw/custom", **kwargs):
        self.data_dir = Path(data_dir)
        # TODO: add any extra constructor args you need

    def get_metadata(self) -> DatasetMetadata:
        return self.METADATA

    def load_ic(self, sample_idx: int = 0) -> dict[str, np.ndarray]:
        """
        Return initial conditions for sample_idx.
        Output: {var_name: np.ndarray of shape spatial_shape}
        """
        # TODO: implement
        # Example — load from numpy file:
        #   data = np.load(self.data_dir / f"ic_{sample_idx:04d}.npy")
        #   return {"u": data[0], "v": data[1]}
        raise NotImplementedError("Implement load_ic() in CustomLoader")

    def load_snapshots(
        self,
        sample_idx: int = 0,
        time_indices: Optional[list[int]] = None,
    ) -> dict[float, dict[str, np.ndarray]]:
        """
        Return ground-truth snapshots.
        Output: {t: {var_name: np.ndarray of shape spatial_shape}}
        """
        # TODO: implement
        # Example — load from HDF5:
        #   import h5py
        #   with h5py.File(self.data_dir / f"sample_{sample_idx:04d}.h5") as f:
        #       u_all = f["u"][:]   # shape (T, H, W)
        #       v_all = f["v"][:]
        #   dt = self.METADATA.dt
        #   indices = time_indices or list(range(self.METADATA.n_time_steps))
        #   return {i * dt: {"u": u_all[i], "v": v_all[i]} for i in indices}
        raise NotImplementedError("Implement load_snapshots() in CustomLoader")
