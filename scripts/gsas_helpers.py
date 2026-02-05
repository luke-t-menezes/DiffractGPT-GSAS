# Import os
import sys, os
from os.path import join
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# Import GSAS-II
# sys.path.insert(0,os.path.expanduser("~/anaconda3/envs/GSASII/GSAS-II/GSASII")) #for Luke's laptop
sys.path.insert(0,os.path.expanduser(r"~\gsas2full\GSAS-II\GSASII"))
import GSASIIscriptable as gs
from GSASIIscriptable import G2Project

# Import constants
from config.constants import GPX_DIRECTORY, CIF_DIRECTORY, XRD_DIRECTORY, INST_PARAM_DIRECTORY


def create_project(data_file:str):
    # Strip any extension and add gpx
    base_name = os.path.splitext(data_file)[0]
    project_file = f'{base_name}.gpx'
    project = gs.G2Project(newgpx=os.path.join(GPX_DIRECTORY, project_file))
    return project


def add_histogram(project:G2Project, data_file:str, inst_param_file:str):
    # Add XRD data (historgam) to the G2Project
    project.add_powder_histogram(data_file, inst_param_file)
    print(f'Added PXRD from {data_file} to the G2Project.')


def add_phase_to_project(project:G2Project, cif_file:str):
    # Phases must be associated with a specific histogram in the G2Project
    hist = project.histogram(0)
    phase = os.path.basename(cif_file).replace('.cif', '')

    # Add phases from CIF files to the G2Project
    project.add_phase(cif_file, phasename=phase, histograms=[hist], fmthint='CIF')
    print(f'Added {project.phase(0).name} to the G2Project.')


def create_refinements(phase_list : list):
    # Refinement Dictionaries    
    REF1 = {'once': {'Background': {'type': 'chebyschev-1', 'refine': True, 'no. coeffs': 5}},
            'clear': {}
            }
    
    # TODO With limits. Make more universal
    # REF1 = {'set': {'Limits': [10.0, 80.0]}, 
    #         'once': {'Background': {'type': 'chebyschev-1', 'refine': True, 'no. coeffs': 5}},
    #         'clear': {}
    #         }
    
    REF2 = {'phases': phase_list,
            'set': {'Cell': True}
            }

    REF3 = {'phases': phase_list,
            'set': {'Scale': True},
            'clear': {'Cell': True}        
            }
    
    # Use 'Phase Fraction': {'Scale': True} for multi-phase samples
    
    REF4 = {'phases': phase_list,
            'set': {'Cell': True,
                    'Sample Parameters': ['Shift']},
            'clear': {'Scale': True},
            }

    REF5 = {'phases': phase_list,
            'set': {'Cell': True,
                    'Size': {'type': 'isotropic', 'refine': True},
                    'Scale': True,
                    'Background': {'type': 'chebyschev-1', 'refine': True, 'no. coeffs': 5}}, 
            'clear': {'Sample Parameters': ['Shift']}
            }
    
    # A list of refinements can be added to GSAS-II for consecutive refinements
    REF_LIST = [REF1, REF2, REF3, REF4, REF5]
    return REF_LIST


def set_controls(project:G2Project, cycles:int = 50, min_delta:float = 0.0001):
    # Set the convergence criteria for the refinement
    # cycles: max number of least square cycles
    # min_delta is how small the difference bewteen least square cycles must be to terminate
    project.set_Controls('cycles', cycles)
    project.data['Controls']['data']['min dM/M'] = min_delta


def run_refinement(project: G2Project, ref_list: list):
    # Run refinement using the consecutive refinements
    project.do_refinements(ref_list, outputnames=None)


def get_refinement_stats(project: G2Project):
    # If a refinement hasn't been run yet the project won't have rwp, rmin to get
    rwp = project.histogram(0).data['data'][0]['wR']
    rmin = project.histogram(0).data['data'][0]['wRmin']
    chi2 = (rwp / rmin) ** 2
    return rwp, rmin, chi2


def build_project(data_file: str, cif_file: str, inst_param_file: str):
    # Build full paths
    data_path = os.path.join(XRD_DIRECTORY, data_file)
    inst_path = os.path.join(INST_PARAM_DIRECTORY, inst_param_file)
    cif_path = os.path.join(CIF_DIRECTORY, cif_file)
    
    # Create project
    project = create_project(data_file)
    
    # Add histogram
    add_histogram(project, data_path, inst_path)
    
    # Add phase
    add_phase_to_project(project, cif_path)
    
    # Set controls
    set_controls(project, cycles=50, min_delta=0.0001)

    # Creat refinement list
    ref_list = create_refinements([project.phase(0).name])

    # Run refinement
    run_refinement(project, ref_list)
    
    return project


def plot_xrd(project:G2Project, hist_number:int=0):
    fig = plt.figure(figsize=(15,12))
    gs = gridspec.GridSpec(3,1, hspace=0)

    panel1 = fig.add_subplot(gs[:-1,:])
    panel1.plot(project.histogram(hist_number).getdata('x'), project.histogram(hist_number).getdata('yobs'), marker='o', linestyle='none', markersize=2, label='Observed', alpha=0.6)
    panel1.plot(project.histogram(hist_number).getdata('x'), project.histogram(hist_number).getdata('ycalc'), label='Calculated')
    panel1.plot(project.histogram(hist_number).getdata('x'), project.histogram(hist_number).getdata('background'), label='Background')
    panel1.set_xticklabels('')
    # panel1.plot(project.histogram(0).getdata('x'), project.histogram(0).getdata('residual'))

    #Note that the .getdata() function can access: 'x', 'yobs', 'yweight', 'ycalc', 'background', 'residual'
    #note that 'yweight' = 1/sigma^2. 
    panel2 = fig.add_subplot(gs[-1,:], sharex=panel1)
    delta_over_sigma = project.histogram(hist_number).getdata('residual')*np.power(project.histogram(hist_number).getdata('yweight'),0.5)
    panel2.plot(project.histogram(hist_number).getdata('x'), delta_over_sigma)
    panel2.set_xlim(xmin=np.min(project.histogram(hist_number).getdata('x')), xmax=np.max(project.histogram(hist_number).getdata('x')))
    panel2.set_ylabel('$\Delta$/$\sigma$')
    panel2.set_xlabel('2$\Theta$')
    panel1.legend()
    plt.show()


def get_xrd_files(directory:str=r'data\xrd'):
    # List all the files in the XRD directory
    files = [f for f in os.listdir(directory)]

    return sorted(files)


def generate_output_names(input_filename:str, base_dir:str='data'):
    # Generate consistent output file paths from input file name
    base = os.path.splitext(os.path.basename(input_filename))[0]

    return {'vasp': os.path.join(base_dir, 'vasp', f'{base}_predicted.vasp'),
            'cif': os.path.join(base_dir, 'cif', f'{base}_predicted.cif'),
            'symmetrized': os.path.join(base_dir, 'cif', f'{base}_symmetrized.vasp'),
            'gpx': os.path.join(base_dir, 'gpx', f'{base}.gpx'),
            }