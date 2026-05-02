import numpy as np

def solver(u0_batch, v0_batch, w0_batch, t_coordinate, tau_d):
    batch_size = u0_batch.shape[0]
    N = 512
    T_output = len(t_coordinate)
    dt = 0.025
    dx = 10.0 / 512.0  # 0.01953125
    dx_sq = dx ** 2

    # Parameters
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

    # Initialize output arrays
    u_pred = np.zeros((batch_size, T_output, N, N), dtype=np.float32)
    v_pred = np.zeros((batch_size, T_output, N, N), dtype=np.float32)
    w_pred = np.zeros((batch_size, T_output, N, N), dtype=np.float32)

    # Set initial conditions
    u_pred[:, 0] = u0_batch.astype(np.float32)
    v_pred[:, 0] = v0_batch.astype(np.float32)
    w_pred[:, 0] = w0_batch.astype(np.float32)

    # Current state
    u_curr = u0_batch.astype(np.float32)
    v_curr = v0_batch.astype(np.float32)
    w_curr = w0_batch.astype(np.float32)

    # Time loop over output times
    for i in range(1, T_output):
        t_prev = t_coordinate[i-1]
        t_current = t_coordinate[i]
        delta_t = t_current - t_prev
        n_steps = int(round(delta_t / dt))

        for step in range(n_steps):
            # Compute Laplacian of u_curr
            u_padded = np.pad(u_curr, ((0, 0), (1, 1), (1, 1)), mode='edge')
            laplacian_u = (
                u_padded[:, 2:, 1:-1] + u_padded[:, :-2, 1:-1] +
                u_padded[:, 1:-1, 2:] + u_padded[:, 1:-1, :-2] -
                4 * u_padded[:, 1:-1, 1:-1]
            ) / dx_sq

            # Compute ionic currents
            mask_u_ge_Vc = (u_curr >= V_c).astype(np.float32)
            I_fi = -v_curr * mask_u_ge_Vc * (u_curr - V_c) * (1 - u_curr) / tau_d

            part1 = u_curr * (1 - mask_u_ge_Vc) / tau_0
            part2 = mask_u_ge_Vc / tau_r
            I_so = part1 + part2

            term = k * (u_curr - V_csi)
            tanh_term = np.tanh(term)
            I_si = -w_curr * (1 + tanh_term) / (2 * tau_si)

            # Compute du_dt
            du_dt = D * laplacian_u - (I_fi + I_so + I_si) / C_m

            # Compute dv_dt
            H_u_Vv = (u_curr >= V_v).astype(np.float32)
            tau_mv = (1 - H_u_Vv) * tau_v1 + H_u_Vv * tau_v2
            mask_u_less_Vc = 1.0 - mask_u_ge_Vc
            dv_dt = mask_u_less_Vc * ((1 - v_curr) / tau_mv) + mask_u_ge_Vc * (-v_curr / tau_pv)

            # Compute dw_dt
            dw_dt = mask_u_less_Vc * ((1 - w_curr) / tau_mw) + mask_u_ge_Vc * (-w_curr / tau_pw)

            # Update variables
            u_curr = u_curr + dt * du_dt
            v_curr = v_curr + dt * dv_dt
            w_curr = w_curr + dt * dw_dt

        # After all steps for this output time, save the current state
        u_pred[:, i] = u_curr
        v_pred[:, i] = v_curr
        w_pred[:, i] = w_curr

    return u_pred, v_pred, w_pred