"""
data/base.py — Abstract data source interface.

All data sources (PDEBench, FK ground truth, custom) implement DataSource.
Use get_data_source() to get the right one by name.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class DatasetMetadata:
    name: str                          # e.g. "pdebench_2d_rd", "fk_tau0.5714"
    n_vars: int                        # number of state variables
    var_names: list[str]               # e.g. ["u", "v", "w"]
    spatial_shape: tuple[int, ...]     # e.g. (512, 512)
    n_time_steps: int                  # snapshots available
    t_start: float
    t_end: float
    dt: float
    dx: float
    domain_size: float                 # e.g. 20.0
    params: dict = field(default_factory=dict)  # model parameters


class DataSource(ABC):
    """
    Abstract base class for all evaluation data sources.

    Subclasses must implement load_ic(), load_snapshots(), and get_metadata().
    All spatial arrays have shape (H, W) for 2D or (N,) for 1D.
    """

    @abstractmethod
    def get_metadata(self) -> DatasetMetadata:
        """Return dataset metadata."""

    @abstractmethod
    def load_ic(self, sample_idx: int = 0) -> dict[str, np.ndarray]:
        """
        Load initial conditions for one sample.
        Returns {var_name: array of shape spatial_shape}.
        """

    @abstractmethod
    def load_snapshots(
        self,
        sample_idx: int = 0,
        time_indices: Optional[list[int]] = None,
    ) -> dict[float, dict[str, np.ndarray]]:
        """
        Load ground-truth snapshots.
        Returns {t: {var_name: array}} for each requested time index.
        If time_indices is None, load all available snapshots.
        """

    def load_training_trajectories(
        self,
        sample_indices: list[int],
        subsample_t: int = 1,
    ) -> tuple[list[dict], DatasetMetadata]:
        """
        Load multiple trajectories for OpInf training.
        Returns (list of {t: {var: array}}, metadata).
        """
        trajectories = []
        for idx in sample_indices:
            snaps = self.load_snapshots(sample_idx=idx)
            if subsample_t > 1:
                times = sorted(snaps.keys())
                snaps = {t: snaps[t] for i, t in enumerate(times) if i % subsample_t == 0}
            trajectories.append(snaps)
        return trajectories, self.get_metadata()


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_data_source(name: str, **kwargs) -> DataSource:
    """
    Factory function. name must be one of:
        "pdebench_2d_rd"   — PDEBench 2D Reaction-Diffusion (FitzHugh-Nagumo)
        "pdebench_1d_burgers" — PDEBench 1D Burgers
        "fk"               — Fenton-Karma ground truth (local CSV/NPZ)
        "custom"           — Custom data source (extend CustomLoader)
    """
    if name == "pdebench_2d_rd":
        from data.pdebench_loader import PDEBench2DRDLoader
        return PDEBench2DRDLoader(**kwargs)
    elif name == "pdebench_1d_burgers":
        from data.pdebench_loader import PDEBench1DBurgersLoader
        return PDEBench1DBurgersLoader(**kwargs)
    elif name == "fk":
        from data.fk_loader import FKDataLoader
        return FKDataLoader(**kwargs)
    elif name == "custom":
        from data.custom_loader import CustomLoader
        return CustomLoader(**kwargs)
    else:
        raise ValueError(
            f"Unknown data source '{name}'. "
            f"Choose from: pdebench_2d_rd, pdebench_1d_burgers, fk, custom"
        )
