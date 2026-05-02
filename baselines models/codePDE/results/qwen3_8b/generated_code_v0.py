import numpy as np

def solver(u0_batch, v0_batch, w0_batch, t_coordinate, tau_d):
    """Solves the Fenton-Karma 3V model.

    Args:
        u0_batch (np.ndarray): Initial condition [batch_size, N, N].
        v0_batch (np.ndarray): Initial condition [batch_size, N, N].
        w0_batch (np.ndarray): Initial condition [batch_size, N, N].
        t_coordinate (np.ndarray): Time coordinates [T+1], starting at t_0=0.
        tau_d (float): The tau_d parameter.

    Returns:
        u_pred (np.ndarray): [batch_size, len(t_coordinate), N, N].
        v_pred (np.ndarray): [batch_size, len(t_coordinate), N, N].
        w_pred (np.ndarray): [batch_size, len(t_coordinate), N, N].
    """
    # Model parameters
    D = 0.001
    C_m = 1.0
    tau_pv = 7.99
    tau_v1 = 9.8
    tau_v2 = 312.5
    tau_pw = 870.0
    tau_mw = 41.0
    tau_0 = 12.5
    tau_r = 33.83
    tau_si = 29.0
    k = 10.0
    V_csi = 0.861
    V_c = 0.13
    V_v = 0.04

    # Spatial discretization
    N = u0_batch.shape[1]
    dx = 20.0 / N  # Domain [-10, 10] with N points

    # Time parameters
    num_time_steps = len(t_coordinate)
    dt = t_coordinate[1] - t_coordinate[0]

    # Initialize output arrays
    u_pred = np.zeros((u0_batch.shape[0], num_time_steps, N, N))
    v_pred = np.zeros((u0_batch.shape[0], num_time_steps, N, N))
    w_pred = np.zeros((u0_batch.shape[0], num_time_steps, N, N))

    # Set initial conditions
    u_pred[:, 0, :, :] = u0_batch
    v_pred[:, 0, :, :] = v0_batch
    w_pred[:, 0, :, :] = w0_batch

    # Time integration
    for t_idx in range(1, num_time_steps):
        for b in range(u0_batch.shape[0]):
            u = u_pred[b, t_idx-1, :, :]
            v = v_pred[b, t_idx-1, :, :]
            w = w_pred[b, t_idx-1, :, :]

            # Compute Laplacian of u
            # x-direction
            u_prev_x = np.zeros_like(u)
            u_prev_x[1:, :] = u[:-1, :]
            u_prev_x[0, :] = u[0, :]
            u_next_x = np.zeros_like(u)
            u_next_x[:-1, :] = u[1:, :]
            u_next_x[-1, :] = u[-1, :]
            u_xx = (u_next_x - 2*u + u_prev_x) / dx**2

            # y-direction
            u_prev_y = np.zeros_like(u)
            u_prev_y[:, 1:] = u[:, :-1]
            u_prev_y[:, 0] = u[:, 0]
            u_next_y = np.zeros_like(u)
            u_next_y[:, :-1] = u[:, 1:]
            u_next_y[:, -1] = u[:, -1]
            u_yy = (u_next_y - 2*u + u_prev_y) / dx**2

            laplacian_u = u_xx + u_yy

            # Compute ionic currents
            H_c = (u >= V_c).astype(np.float64)
            I_fi = -v * H_c * (u - V_c) * (1 - u) / tau_d
            H_so = 1 - H_c
            I_so = u * H_so / tau_0 + H_c / tau_r
            tanh_term = np.tanh(k * (u - V_csi))
            I_si = -w * (1 + tanh_term) / (2 * tau_si)

            # RHS for u
            RHS_u = D * laplacian_u - (I_fi + I_so + I_si) / C_m

            # RHS for v
            H_v = (u >= V_v).astype(np.float64)
            tau_mv = (1 - H_v) * tau_v1 + H_v * tau_v2
            H_c_v = (u >= V_c).astype(np.float64)
            RHS_v = np.where(H_c_v, -v / tau_pv, (1 - v) / tau_mv)

            # RHS for w
            RHS_w = np.where(H_c_v, -w / tau_pw, (1 - w) / tau_mw)

            # Update variables
            u_new = u + dt * RHS_u
            v_new = v + dt * RHS_v
            w_new = w + dt * RHS_w

            u_pred[b, t_idx, :, :] = u_new
            v_pred[b, t_idx, :, :] = v_new
            w_pred[b, t_idx, :, :] = w_new

    return u_pred, v_pred, w_pred