from pymatgen.core import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
import os.path



def symmetrize_structure(input_cif:str, output_cif:str, symprec: float =0.1):
    # Find and apply the correct symmetry to the structure using Pymatgen
    # symprec (symmetry precision) 0.1 angstrom tolerance

    # Read the primitive (P1 triclinic) CIF
    structure = Structure.from_file(input_cif)

    # Find and apply symmetries
    sga = SpacegroupAnalyzer(structure, symprec=symprec)

    # Get the symmetrized structure
    symmetrized = sga.get_refined_structure()

    os.makedirs(os.path.dirname(output_cif), exist_ok=True)
    symmetrized.to(filename=output_cif, fmt='cif', symprec=symprec)

    # Print symmetry info
    print(f"Space group: {sga.get_space_group_symbol()}")
    print(f"Space group number: {sga.get_space_group_number()}")

    return output_cif




