from agapi.client import Agapi
from ase.io import read, write
import os.path


def predict_cif_from_data(api_key:str, data_file:str, output_paths:dict):
    # Predict structure from CIF and configure output paths
    
    # Initialize client
    client = Agapi(api_key)

    # Query with your XRD FILE
    print('Sending XRD data to AtomGPT.org...')
    result = client.pxrd_query(file_path=data_file)

    # Save VASP
    os.makedirs(os.path.dirname(output_paths['vasp']), exist_ok=True)
    with open(output_paths['vasp'], 'w') as f:
        f.write(result)

    # Convert to CIF
    os.makedirs(os.path.dirname(output_paths['cif']), exist_ok=True)
    structure = read(output_paths['vasp'], format='vasp')
    write(output_paths['cif'], structure)

    return output_paths['cif']


