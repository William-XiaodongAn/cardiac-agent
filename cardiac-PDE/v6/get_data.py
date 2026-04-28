import requests
import os
import pickle
import h5py
import numpy as np

# download data from pdeBench
links = {}
pde_names = {}
paras = {}

links['1D_Advection_Sols_beta0.1.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/255672'
pde_names['1D_Advection_Sols_beta0.1.hdf5'] = 'advection_beta0.1'
paras['1D_Advection_Sols_beta0.1.hdf5'] = {'beta': 0.1}

links['1D_Advection_Sols_beta1.0.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/255675'
pde_names['1D_Advection_Sols_beta1.0.hdf5'] = 'advection_beta1.0'
paras['1D_Advection_Sols_beta1.0.hdf5'] = {'beta': 1.0}

links['1D_Burgers_Sols_Nu0.001.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/268190'
pde_names['1D_Burgers_Sols_Nu0.001.hdf5'] = 'burgers_nu0.001'
paras['1D_Burgers_Sols_Nu0.001.hdf5'] = {'nu': 0.001}

links['1D_Burgers_Sols_Nu1.0.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/281365'
pde_names['1D_Burgers_Sols_Nu1.0.hdf5'] = 'burgers_nu1.0'
paras['1D_Burgers_Sols_Nu1.0.hdf5'] = {'nu': 1.0}   

links['2D_diff-react_NA_NA.h5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/133017'
pde_names['2D_diff-react_NA_NA.h5'] = 'twoD_reaction_diffusion'
paras['2D_diff-react_NA_NA.h5'] = {    "D_u": 0.001,    "D_v": 0.005,    "k": 0.005} 

links['fk.h5'] = ''
pde_names['fk.h5'] = 'fenton_karma'
paras['fk.h5'] = {} 

def transform_1D_to_2D(data_1D, xcoor):
    data_1D_to = data_1D[0]
    data_1D_tend = data_1D[-1]
    r_channel = np.tile(data_1D_to, (len(xcoor), 1))
    g_channel = np.zeros_like(r_channel)
    b_channel = np.zeros_like(r_channel)
    a_channel = np.zeros_like(r_channel)

    rgba_flat = np.dstack([r_channel, g_channel, b_channel, a_channel]).ravel()
    
    r_channel = np.tile(data_1D_tend, (len(xcoor), 1))
    g_channel = np.zeros_like(r_channel)
    b_channel = np.zeros_like(r_channel)
    a_channel = np.zeros_like(r_channel)

    rgba_flat_tend = np.dstack([r_channel, g_channel, b_channel, a_channel]).ravel()
    return rgba_flat.reshape(1, -1),rgba_flat_tend.reshape(1, -1)

def main():
    for filename in links.keys():
        
        url = links[filename]
        pde_name = pde_names[filename]
        para = paras[filename]
        
        # Define and create the directory if it doesn't exist
        path = os.path.join('data', pde_name)
        os.makedirs(f"./data/{pde_name}/train", exist_ok=True)
        os.makedirs(f"./data/{pde_name}/test", exist_ok=True)
        print(f"Downloading {filename}...")
        hdf5_file_name = pde_name + '.hdf5'
        try:
            # Send request
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the HDF5 file

            file_save_path = os.path.join(path, hdf5_file_name)
            with open(file_save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Save the parameters with pickle
            pickle_name = hdf5_file_name.replace('.hdf5', '_paras.pkl')
            with open(os.path.join(path, pickle_name), 'wb') as f:
                pickle.dump(para, f)
                
            print(f"Successfully saved to {path}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading {filename}: {e}")
            return
    
    # now read the data and split into train and test sets, and save them to corresponding folders
    
        if filename != '2D_diff-react_NA_NA.h5' and filename != 'fk.h5':
            # take 2 samples as test set and 50 sample as train set
            hdf5_file_path = f"./data/{pde_name}/{hdf5_file_name}"
            
            with h5py.File(hdf5_file_path, 'r') as f:
                
                data = f['tensor'][:] 
                tcoor = f['t-coordinate'][:]
                xcoor = f['x-coordinate'][:]
            
            random_indices = np.random.choice(data.shape[0], size=52, replace=False)
            random_samples = data[random_indices]
            
            # save IC
            for i in range(52):
                sample_2D, sample_2D_tend = transform_1D_to_2D(random_samples[i], xcoor)
                if i < 2:
                    IC_file = f'./data/{pde_name}/train/IC_{i}.csv'
                else:
                    IC_file = f'./data/{pde_name}/test/IC_{i}.csv'
                with open(IC_file, 'w') as f:
                    # Header: width,height, (matching the JS comma logic)
                    f.write(f"{random_samples.shape[2]},{random_samples.shape[2]},")
                    
                    # Save the flattened array as a single row
                    np.savetxt(f, sample_2D, delimiter=",", fmt="%.10e")
                
                with open(IC_file.replace('IC', 'solution'), 'w') as f:
                    f.write(f"{random_samples.shape[2]},{random_samples.shape[2]},")
                    np.savetxt(f, sample_2D_tend, delimiter=",", fmt="%.10e")
                    
        elif filename == '2D_diff-react_NA_NA.h5':
            hdf5_file_path = f"./data/{pde_name}/{hdf5_file_name}"
            
            with h5py.File(hdf5_file_path, 'r') as f:
                all_keys = list(f.keys())
                random_keys = np.random.choice(all_keys, size=102, replace=False)
                sampled_data_list = [f[key]['data'][:] for key in random_keys]
                random_samples = np.stack(sampled_data_list)

            # save IC
            for i in range(102):
                sample_2D = random_samples[i][0]
                sample_2D_tend = random_samples[i][-1]
                if i < 2:
                    IC_file = f'./data/{pde_name}/train/IC_{i}.csv'
                else: 
                    IC_file = f'./data/{pde_name}/test/IC_{i}.csv'
                with open(IC_file, 'w') as f:
                    # Header: width,height, (matching the JS comma logic)
                    f.write(f"{sample_2D.shape[0]},{sample_2D.shape[1]},")
                    rgba = np.zeros((sample_2D.shape[0], sample_2D.shape[1], 4), dtype=sample_2D.dtype)
                    rgba[..., 0] = sample_2D[..., 0] # Set R
                    rgba[..., 1] = sample_2D[..., 1] # Set G
                    flat_rgba = rgba.flatten()

                    np.savetxt(f, flat_rgba.reshape(1, -1), delimiter=",", fmt="%.10e")
                
                with open(IC_file.replace('IC', 'solution'), 'w') as f:
                    f.write(f"{sample_2D_tend.shape[0]},{sample_2D_tend.shape[1]},")
                    rgba = np.zeros((sample_2D_tend.shape[0], sample_2D_tend.shape[1], 4), dtype=sample_2D_tend.dtype)
                    rgba[..., 0] = sample_2D_tend[..., 0] # Set R
                    rgba[..., 1] = sample_2D_tend[..., 1] # Set G
                    flat_rgba = rgba.flatten()

                    np.savetxt(f, flat_rgba.reshape(1, -1), delimiter=",", fmt="%.10e")
                    
if __name__ == "__main__":
    main()