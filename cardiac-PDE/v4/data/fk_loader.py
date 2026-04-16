"""
data/fk_loader.py — Fenton-Karma ground truth data loader.

Wraps the existing CSV/NPZ files in baselines models/fk_data/tau_d_0.5714/
with the standard DataSource interface so it can be swapped with PDEBench.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

import numpy as np

from data.base import DataSource, DatasetMetadata

_DEFAULT_FK_DIR = Path("../baselines models/fk_data")

FK_SNAPSHOT_TIMES = [
    831.25, 841.25, 851.25, 861.25, 871.25,
    881.25, 891.25, 901.25, 911.25, 921.25, 931.25,
]


class FKDataLoader(DataSource):
    """
    Fenton-Karma 3V ground truth.

    Data layout (tau_d_0.5714/):
        IC.csv              — flattened (512*512, 4) initial conditions
        UVW_array_data.npz  — arrays U,V,W of shape (11, 512, 512)
        sim_data_{T}.csv    — per-snapshot at T in FK_SNAPSHOT_TIMES

    DataSource interface maps sample_idx=0 to the single available trajectory.
    """

    def __init__(
        self,
        data_dir: str = str(_DEFAULT_FK_DIR),
        tau_d: float = 0.5714,
        n: int = 512,
    ):
        self.data_dir = Path(data_dir)
        self.tau_d = tau_d
        self.n = n
        self._subdir = self.data_dir / f"tau_d_{tau_d}"
        self._npz: Optional[dict] = None
        self._ic: Optional[dict] = None

    def _load_npz(self):
        if self._npz is not None:
            return
        npz_path = self._subdir / "UVW_array_data.npz"
        if npz_path.exists():
            raw = np.load(npz_path)
            self._npz = {
                t: {"u": raw["U"][i], "v": raw["V"][i], "w": raw["W"][i]}
                for i, t in enumerate(FK_SNAPSHOT_TIMES)
            }
        else:
            # Fall back to individual CSV files
            self._npz = {}
            n = self.n
            for t in FK_SNAPSHOT_TIMES:
                csv_path = self._subdir / f"sim_data_{t}.csv"
                if csv_path.exists():
                    data = np.loadtxt(csv_path, delimiter=",")
                    self._npz[t] = {
                        "u": data[:, 0].reshape(n, n),
                        "v": data[:, 1].reshape(n, n),
                        "w": data[:, 2].reshape(n, n),
                    }

    def get_metadata(self) -> DatasetMetadata:
        n = self.n
        return DatasetMetadata(
            name=f"fk_tau{self.tau_d}",
            n_vars=3,
            var_names=["u", "v", "w"],
            spatial_shape=(n, n),
            n_time_steps=len(FK_SNAPSHOT_TIMES),
            t_start=FK_SNAPSHOT_TIMES[0],
            t_end=FK_SNAPSHOT_TIMES[-1],
            dt=0.025,
            dx=20.0 / n,
            domain_size=20.0,
            params={
                "D": 0.001, "C_m": 1.0, "tau_d": self.tau_d,
                "tau_pv": 7.99, "V_c": 0.13,
            },
        )

    def load_ic(self, sample_idx: int = 0) -> dict[str, np.ndarray]:
        ic_path = self._subdir / "IC.csv"
        n = self.n
        if ic_path.exists():
            data = np.loadtxt(ic_path, delimiter=",")
            return {
                "u": data[:, 0].reshape(n, n),
                "v": data[:, 1].reshape(n, n),
                "w": data[:, 2].reshape(n, n),
            }
        # If no IC file, return zero initial condition
        return {v: np.zeros((n, n)) for v in ["u", "v", "w"]}

    def load_snapshots(
        self,
        sample_idx: int = 0,
        time_indices: Optional[list[int]] = None,
    ) -> dict[float, dict[str, np.ndarray]]:
        self._load_npz()
        all_times = FK_SNAPSHOT_TIMES
        if time_indices is not None:
            times = [all_times[i] for i in time_indices if i < len(all_times)]
        else:
            times = all_times
        return {t: self._npz[t] for t in times if t in self._npz}
