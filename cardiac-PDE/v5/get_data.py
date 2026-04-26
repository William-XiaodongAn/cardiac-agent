import requests
import os
import pickle

# download data from pdeBench
links = {}
pde_names = {}
paras = {}

links['1D_Advection_Sols_beta0.1.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/255672'
pde_names['1D_Advection_Sols_beta0.1.hdf5'] = 'advection'
paras['1D_Advection_Sols_beta0.1.hdf5'] = {'beta': 0.1}

links['1D_Advection_Sols_beta1.0.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/255675'
pde_names['1D_Advection_Sols_beta1.0.hdf5'] = 'advection'
paras['1D_Advection_Sols_beta1.0.hdf5'] = {'beta': 1.0}

links['1D_Burgers_Sols_Nu0.001.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/268190'
pde_names['1D_Burgers_Sols_Nu0.001.hdf5'] = 'burgers'
paras['1D_Burgers_Sols_Nu0.001.hdf5'] = {'nu': 0.001}

links['1D_Burgers_Sols_Nu1.0.hdf5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/281365'
pde_names['1D_Burgers_Sols_Nu1.0.hdf5'] = 'burgers'
paras['1D_Burgers_Sols_Nu1.0.hdf5'] = {'nu': 1.0}   

links['2D_diff-react_NA_NA.h5'] = 'https://darus.uni-stuttgart.de/api/access/datafile/133017'
pde_names['2D_diff-react_NA_NA.h5'] = 'twoD_reaction_diffusion'
paras['2D_diff-react_NA_NA.h5'] = {} 

def main():
    for filename in links.keys():
        url = links[filename]
        name = pde_names[filename]
        para = paras[filename]
        
        # Define and create the directory if it doesn't exist
        path = os.path.join('data', name)
        os.makedirs(path, exist_ok=True)
        
        print(f"Downloading {filename}...")
        
        try:
            # Send request
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Save the HDF5 file
            file_save_path = os.path.join(path, filename)
            with open(file_save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Save the parameters with pickle
            pickle_name = filename.replace('.hdf5', '_paras.pkl')
            with open(os.path.join(path, pickle_name), 'wb') as f:
                pickle.dump(para, f)
                
            print(f"Successfully saved to {path}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading {filename}: {e}")

if __name__ == "__main__":
    main()