"""
data/pdebench_loader.py — PDEBench data loaders.

PDEBench: https://github.com/pdebench/PDEBench
Data DOI:  https://doi.org/10.18419/darus-2986

HDF5 array layout: [N, T, X, (Y), V]
  N = number of samples (trajectories)
  T = number of time steps
  X, Y = spatial dimensions
  V = number of variables (channels)

Download instructions
---------------------
Option A — pip (small datasets only):
    pip install pdebench

Option B — direct download from DaRUS:
    See CHANGES.md §Setup for wget commands for each dataset file.

Option C — HuggingFace datasets API:
    pip install datasets huggingface_hub
    huggingface-cli download pdebench/pdebench <file.hdf5> --local-dir ./data/raw/
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

import numpy as np

from data.base import DataSource, DatasetMetadata

# Default local path — override with PDEBENCH_DATA_DIR env var or constructor arg
_DEFAULT_DATA_DIR = Path(os.environ.get("PDEBENCH_DATA_DIR", "./data/raw/pdebench"))


class PDEBench2DRDLoader(DataSource):
    """
    2D Reaction-Diffusion (FitzHugh-Nagumo) from PDEBench.

    File: 2D/diffusion-reaction/2D_diff-react_NA_NA.h5
    Shape: [N, T, X, Y, V] = [N, 101, 128, 128, 2]  (downsampled)
              or             = [N, 501, 512, 512, 2]  (full resolution)

    Variables: V=0 → activator u,  V=1 → inhibitor v
    Parameters: Du=1e-3, Dv=5e-3, k=5e-3
    Time: T=0..5.0 (101 steps at dt=0.05, or 501 steps at dt=0.01)
    Space: x,y ∈ [0,1]², dx=1/128 or 1/512
    """

    FILENAME = "2D_diff-react_NA_NA.h5"
    # DaRUS direct download URL
    DOWNLOAD_URL = (
        "https://darus.uni-stuttgart.de/api/access/datafile/"
        ":persistentId/?persistentId=doi:10.18419/darus-2986/7"
    )

    def __init__(
        self,
        data_dir: str = str(_DEFAULT_DATA_DIR),
        resolution: str = "low",  # "low" (128×128) or "high" (512×512)
        tau_d: Optional[float] = None,  # unused for PDEBench, kept for API compat
    ):
        self.data_dir = Path(data_dir)
        self.resolution = resolution
        self._h5 = None
        self._data = None

    def _ensure_loaded(self):
        if self._data is not None:
            return
        path = self.data_dir / self.FILENAME
        if not path.exists():
            raise FileNotFoundError(
                f"PDEBench 2D-RD file not found: {path}\n"
                f"Download it with:\n"
                f"  wget -O {path} '{self.DOWNLOAD_URL}'\n"
                f"Or see CHANGES.md §Setup for full instructions."
            )
        import h5py
        self._h5 = h5py.File(path, "r")
        # Key is dataset-specific; inspect with list(self._h5.keys())
        key = list(self._h5.keys())[0]
        self._data = self._h5[key]  # shape [N, T, X, Y, V]
        self._N, self._T, self._X, self._Y, self._V = self._data.shape

    def get_metadata(self) -> DatasetMetadata:
        self._ensure_loaded()
        nx = self._X
        dt = 5.0 / (self._T - 1)
        dx = 1.0 / nx
        return DatasetMetadata(
            name="pdebench_2d_rd",
            n_vars=2,
            var_names=["u", "v"],
            spatial_shape=(nx, nx),
            n_time_steps=self._T,
            t_start=0.0,
            t_end=5.0,
            dt=dt,
            dx=dx,
            domain_size=1.0,
            params={"Du": 1e-3, "Dv": 5e-3, "k": 5e-3},
        )

    def load_ic(self, sample_idx: int = 0) -> dict[str, np.ndarray]:
        self._ensure_loaded()
        frame = self._data[sample_idx, 0, :, :, :]  # (X, Y, V)
        return {"u": frame[:, :, 0], "v": frame[:, :, 1]}

    def load_snapshots(
        self,
        sample_idx: int = 0,
        time_indices: Optional[list[int]] = None,
    ) -> dict[float, dict[str, np.ndarray]]:
        self._ensure_loaded()
        dt = 5.0 / (self._T - 1)
        indices = time_indices if time_indices is not None else list(range(self._T))
        result = {}
        for ti in indices:
            frame = self._data[sample_idx, ti, :, :, :]  # (X, Y, V)
            t = round(ti * dt, 6)
            result[t] = {"u": frame[:, :, 0], "v": frame[:, :, 1]}
        return result

    def __del__(self):
        if self._h5 is not None:
            try:
                self._h5.close()
            except Exception:
                pass


class PDEBench1DBurgersLoader(DataSource):
    """
    1D Burgers' equation from PDEBench.

    File: 1D/Burgers/Train/1D_Burgers_Sols_Nu{nu}.hdf5
    Shape: [N, T, X, V] = [N, 201, 1024, 1]
    Variable: V=0 → u (velocity field)
    Parameters: nu ∈ {0.001, 0.01, 0.1, 1.0}
    Time: T=0..2.0 (201 steps, dt=0.01)
    Space: x ∈ [-1,1], dx=2/1024
    """

    def __init__(
        self,
        data_dir: str = str(_DEFAULT_DATA_DIR),
        nu: float = 0.01,
        split: str = "Train",
    ):
        self.data_dir = Path(data_dir)
        self.nu = nu
        self.split = split
        self._h5 = None
        self._data = None

    @property
    def _filepath(self) -> Path:
        nu_str = str(self.nu).replace(".", "")
        return self.data_dir / "1D" / "Burgers" / self.split / f"1D_Burgers_Sols_Nu{self.nu}.hdf5"

    def _ensure_loaded(self):
        if self._data is not None:
            return
        path = self._filepath
        if not path.exists():
            raise FileNotFoundError(
                f"PDEBench 1D Burgers file not found: {path}\n"
                f"See CHANGES.md §Setup for download instructions."
            )
        import h5py
        self._h5 = h5py.File(path, "r")
        key = list(self._h5.keys())[0]
        self._data = self._h5[key]
        self._N, self._T, self._X, self._V = self._data.shape

    def get_metadata(self) -> DatasetMetadata:
        self._ensure_loaded()
        return DatasetMetadata(
            name=f"pdebench_1d_burgers_nu{self.nu}",
            n_vars=1,
            var_names=["u"],
            spatial_shape=(self._X,),
            n_time_steps=self._T,
            t_start=0.0,
            t_end=2.0,
            dt=2.0 / (self._T - 1),
            dx=2.0 / self._X,
            domain_size=2.0,
            params={"nu": self.nu},
        )

    def load_ic(self, sample_idx: int = 0) -> dict[str, np.ndarray]:
        self._ensure_loaded()
        return {"u": self._data[sample_idx, 0, :, 0]}

    def load_snapshots(
        self,
        sample_idx: int = 0,
        time_indices: Optional[list[int]] = None,
    ) -> dict[float, dict[str, np.ndarray]]:
        self._ensure_loaded()
        dt = 2.0 / (self._T - 1)
        indices = time_indices if time_indices is not None else list(range(self._T))
        return {
            round(ti * dt, 6): {"u": self._data[sample_idx, ti, :, 0]}
            for ti in indices
        }

    def __del__(self):
        if self._h5 is not None:
            try:
                self._h5.close()
            except Exception:
                pass
