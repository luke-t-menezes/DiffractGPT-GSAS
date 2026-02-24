from agapi.agents.client import AGAPIClient
from agapi.agents.functions import pxrd_match, diffractgpt_predict
from ase.io import read, write
import os.path
import pandas as pd


def predict_cif_from_data(api_key:str, formula:str, data_file:str, output_paths:dict, verbose:bool=False, max_points:int=1000):
    # Predict structure from CIF and configure output paths

    # Initialize client
    client = AGAPIClient(api_key)

    # Query with your XRD FILE
    print('Sending XRD data to AtomGPT.org...')
    with open(data_file, 'r') as f:
        lines = f.readlines()
    # Skip non-data header lines (lines that don't start with a number)
    data_lines = [l for l in lines if l.strip() and l.strip()[0].isdigit()]

    # Downsample to avoid exceeding URL length limits (API uses GET requests)
    if len(data_lines) > max_points:
        step = len(data_lines) // max_points
        data_lines = data_lines[::step]
    pattern_data = ''.join(data_lines)
    result = pxrd_match(formula, pattern_data, api_client=client)

    if "matched_poscar" not in result:
        raise ValueError(f"No matched structure returned. API response: {result}")

    # Save VASP
    os.makedirs(os.path.dirname(output_paths['vasp']), exist_ok=True)
    with open(output_paths['vasp'], 'w') as f:
        f.write(result["matched_poscar"])

    # Convert to CIF
    os.makedirs(os.path.dirname(output_paths['cif']), exist_ok=True)
    structure = read(output_paths['vasp'], format='vasp')
    write(output_paths['cif'], structure)

    if verbose:
        print(f'Pattern data: {pattern_data}')

    return output_paths['cif']


def csv_to_two_column(csv_path:str, output_path:str, header:str, col1=0, col2=1, skiprows=1):
    # DiffractGPT like's 2 column data
    # use ' ' delimeter

    df = pd.read_csv(csv_path, skiprows=skiprows)
    
    # Extract two columns
    data = df.iloc[:, [col1, col2]]
    
    # Write with space delimiter, no header
    data.to_csv(output_path, sep=' ', index=False, header=header)


