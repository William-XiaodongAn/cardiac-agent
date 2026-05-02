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

    # Extract spatial grid size
    N = u0_batch.shape[1]
    dx = 20.0 / N  # Spatial step size

    # Preallocate output arrays
    batch_size = u0_batch.shape[0]
    T = len(t_coordinate) - 1  # Number of time steps
    u_pred = np.zeros([batch_size, T+1, N, N])
    v_pred = np.zeros([batch_size, T+1, N, N])
    w_pred = np.zeros([batch_size, T+1, N, N])

    # Initialize with initial conditions
    for b in range(batch_size):
        u_pred[b, 0, :, :] = u0_batch[b, :, :]
        v_pred[b, 0, :, :] = v0_batch[b, :, :]
        w_pred[b, 0, :, :] = w0_batch[b, :, :]

    # Helper function to compute Laplacian using finite differences
    def compute_laplacian(u):
        N = u.shape[0]
        d2u_dx2 = np.zeros_like(u)
        d2u_dx2[0, :] = (u[1, :] - u[0, :]) / dx**2
        d2u_dx2[N-1, :] = (u[N-2, :] - u[N-1, :]) / dx**2
        d2u_dx2[1:N-1, :] = (u[2:N, :] + u[0:N-2, :] - 2*u[1:N-1, :]) / dx**2

        d2u_dy2 = np.zeros_like(u)
        d2u_dy2[:, 0] = (u[:, 1] - u[:, 0]) / dx**2
        d2u_dy2[:, N-1] = (u[:, N-2] - u[:, N-1]) / dx**2
        d2u_dy2[:, 1:N-1] = (u[:, 2:N] + u[:, 0:N-2] - 2*u[:, 1:N-1]) / dx**2

        laplacian = d2u_dx2 + d2u_dy2
        return laplacian

    # Iterate over time steps
    for t in range(1, T+1):
        current_time = t_coordinate[t]
        previous_time = t_coordinate[t-1]
        dt = current_time - previous_time

        for b in range(batch_size):
            u = u_pred[b, t-1, :, :]
            v = v_pred[b, t-1, :, :]
            w = w_pred[b, t-1, :, :]

            # Compute Laplacian for u
            laplacian_u = compute_laplacian(u)

            # Compute ionic currents
            mask_u_less_Vc = (u < V_c)
            I_fi = (-v * mask_u_less_Vc * (u - V_c) * (1 - u)) / tau_d

            # Corrected I_so calculation
            I_so_part1 = u * (1 - mask_u_less_Vc) / tau_0
            I_so_part2 = (1 / tau_r) * mask_u_less_Vc
            I_so = I_so_part1 + I_so_part2

            tanh_term = np.tanh(k * (u - V_csi))
            I_si = -w * (1 + tanh_term) / (2 * tau_si)

            # Update u
            rhs_u = D * laplacian_u - (I_fi + I_so + I_si) / C_m
            u_new = u + dt * rhs_u

            # Update v
            mask_u_less_Vv = (u < V_v)
            tau_mv = (1 - mask_u_less_Vv) * tau_v1 + mask_u_less_Vv * tau_v2
            mask_v_condition = (u < V_c)
            dv_dt = np.zeros_like(v)
            dv_dt[mask_v_condition] = (1 - v[mask_v_condition]) / tau_mv[mask_v_condition]
            dv_dt[~mask_v_condition] = -v[~mask_v_condition] / tau_pv
            v_new = v + dt * dv_dt

            # Update w
            mask_w_condition = (u < V_c)
            dw_dt = np.zeros_like(w)
            dw_dt[mask_w_condition] = (1 - w[mask_w_condition]) / tau_mw
            dw_dt[~mask_w_condition] = -w[~mask_w_condition] / tau_pw
            w_new = w + dt * dw_dt

            # Store new values
            u_pred[b, t, :, :] = u_new
            v_pred[b, t, :, :] = v_new
            w_pred[b, t, :, :] = w_new

    return u_pred, v_pred, w_pred