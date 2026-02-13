from agapi.client import Agapi
from ase.io import read, write
import os.path
import pandas as pd


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


def csv_to_two_column(csv_path:str, output_path:str, header:str, col1=0, col2=1, skiprows=1):
    # DiffractGPT like's 2 column data
    # use ' ' delimeter

    df = pd.read_csv(csv_path, skiprows=skiprows)
    
    # Extract two columns
    data = df.iloc[:, [col1, col2]]
    
    # Write with space delimiter, no header
    data.to_csv(output_path, sep=' ', index=False, header=header)


