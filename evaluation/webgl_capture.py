"""
webgl_capture.py — Capture pixel data from a running WebGL cardiac simulation
using Playwright (headless Chromium).

The WebGL simulation encodes state as RGBA texture:
    R = u (transmembrane potential)
    G = v (fast gating variable)
    B = w (slow gating variable)
    A = unused

Usage:
    from webgl_capture import WebGLCapture
    cap = WebGLCapture("../cardiac-PDE/v1/outputs/fenton_karma/3V MODEL skeleton.html")
    snapshots = cap.run(sample_times=[831.25, 841.25, ..., 931.25], fps_sample=True)
"""

import asyncio
import base64
import json
import time
import numpy as np
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# JavaScript helpers injected into the browser page
# ---------------------------------------------------------------------------

_JS_INJECT = """
window.__webpde_snapshots = {};
window.__webpde_fps_samples = [];
window.__webpde_frame_count = 0;
window.__webpde_last_ts = performance.now();

// Monkey-patch requestAnimationFrame to count frames
const _raf = window.requestAnimationFrame.bind(window);
window.requestAnimationFrame = function(cb) {
    return _raf(function(ts) {
        window.__webpde_frame_count++;
        const dt = ts - window.__webpde_last_ts;
        if (dt > 500) {
            window.__webpde_fps_samples.push(1000.0 / (dt / window.__webpde_frame_count));
            window.__webpde_frame_count = 0;
            window.__webpde_last_ts = ts;
        }
        cb(ts);
    });
};

// Function called by Python to capture current canvas state
window.__webpde_capture = function(tag) {
    const canvas = document.querySelector('canvas');
    if (!canvas) return null;
    const dataUrl = canvas.toDataURL('image/png');
    window.__webpde_snapshots[tag] = dataUrl;
    return tag;
};

// Function to get current simulation time from global abubu variable
window.__webpde_sim_time = function() {
    try { return typeof time !== 'undefined' ? time : null; } catch(e) { return null; }
};
"""

_JS_READ_PIXELS = """
(function() {
    const canvas = document.querySelector('canvas');
    if (!canvas) return null;
    const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!gl) return null;
    const w = canvas.width, h = canvas.height;
    const pixels = new Uint8Array(w * h * 4);
    gl.readPixels(0, 0, w, h, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    // Convert to base64 for transfer
    let binary = '';
    for (let i = 0; i < pixels.length; i++) binary += String.fromCharCode(pixels[i]);
    return {w, h, data: btoa(binary)};
})()
"""


# ---------------------------------------------------------------------------
# Capture class
# ---------------------------------------------------------------------------

class WebGLCapture:
    """
    Runs a WebGL cardiac simulation in headless Chromium and captures
    pixel data at specified simulation times.
    """

    def __init__(
        self,
        html_path: str,
        wait_s_per_time_unit: float = 0.0005,
        canvas_size: int = 512,
    ):
        """
        Args:
            html_path: path to the WebGL HTML file
            wait_s_per_time_unit: wall-clock seconds per simulation time unit
                (tune so the sim reaches the target time before capture)
            canvas_size: expected canvas dimension (default 512)
        """
        self.html_path = str(Path(html_path).resolve())
        self.wait_per_tu = wait_s_per_time_unit
        self.canvas_size = canvas_size

    async def _capture_async(
        self,
        sample_times: list[float],
        fps_duration_s: float = 60.0,
    ) -> dict:
        from playwright.async_api import async_playwright

        results = {"snapshots": {}, "fps": None, "perf": {}}
        t0 = time.perf_counter()

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=True,
                args=["--enable-gpu", "--use-gl=swiftshader",
                      "--disable-software-rasterizer", "--no-sandbox"],
            )
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1280, "height": 900})

            # Load simulation
            await page.goto(f"file://{self.html_path}", wait_until="networkidle")
            await page.evaluate(_JS_INJECT)
            await page.wait_for_timeout(2000)  # let WebGL initialise

            # Capture at each sample time
            sorted_times = sorted(sample_times)
            prev_t = 0.0
            for target_t in sorted_times:
                wait_ms = int((target_t - prev_t) * self.wait_per_tu * 1000)
                wait_ms = max(wait_ms, 500)
                await page.wait_for_timeout(wait_ms)

                # Read raw WebGL RGBA pixels
                pixel_data = await page.evaluate(_JS_READ_PIXELS)
                if pixel_data:
                    w, h = pixel_data["w"], pixel_data["h"]
                    raw = base64.b64decode(pixel_data["data"])
                    arr = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
                    # Flip vertically (WebGL origin is bottom-left)
                    arr = arr[::-1]
                    # Normalize from [0,255] to [0,1] float
                    u_field = arr[:, :, 0].astype(np.float32) / 255.0
                    v_field = arr[:, :, 1].astype(np.float32) / 255.0
                    w_field = arr[:, :, 2].astype(np.float32) / 255.0
                    results["snapshots"][target_t] = {
                        "u": u_field,
                        "v": v_field,
                        "w": w_field,
                    }
                    print(f"  Captured T={target_t:.2f}  u∈[{u_field.min():.3f},{u_field.max():.3f}]")
                else:
                    print(f"  [WARN] No pixel data at T={target_t:.2f}")
                prev_t = target_t

            # FPS measurement
            if fps_duration_s > 0:
                print(f"  Measuring FPS for {fps_duration_s}s...")
                fps_start_frames = await page.evaluate("window.__webpde_frame_count")
                fps_t0 = time.perf_counter()
                await page.wait_for_timeout(int(fps_duration_s * 1000))
                fps_end_frames = await page.evaluate("window.__webpde_frame_count")
                elapsed = time.perf_counter() - fps_t0
                results["fps"] = round((fps_end_frames - fps_start_frames) / elapsed, 1)

            await browser.close()

        results["perf"]["wall_time_s"] = round(time.perf_counter() - t0, 2)
        return results

    def run(
        self,
        sample_times: list[float],
        fps_duration_s: float = 60.0,
    ) -> dict:
        """
        Blocking interface. Returns the same dict as _capture_async.
        """
        return asyncio.run(self._capture_async(sample_times, fps_duration_s))


# ---------------------------------------------------------------------------
# Pixel → numpy array from saved PNG (for offline analysis)
# ---------------------------------------------------------------------------

def png_to_uvw(png_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load a PNG screenshot saved by the WebGL simulation and extract
    the u, v, w fields from the R, G, B channels (normalized to [0,1]).
    """
    from PIL import Image
    img = np.array(Image.open(png_path)).astype(np.float32) / 255.0
    return img[:, :, 0], img[:, :, 1], img[:, :, 2]
