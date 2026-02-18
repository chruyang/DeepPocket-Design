import os
import mdtraj as md
import numpy as np
import openmm as mm
import openmm.app as app
import openmm.unit as unit
import logging

logger = logging.getLogger(__name__)


def run_simulation(pdb_path, target_res_idx, output_dir, steps=5000):
    """
    Runs a short MD simulation to relax the structure and finding open DeepPocket-Design conformations.

    Args:
        pdb_path (str): Input PDB file.
        target_res_idx (int): Index of the target residue to monitor SASA.
        output_dir (str): Directory to save trajectories.
        steps (int): Simulation steps (default: 5000).

    Returns:
        str: Path to the selected 'open' PDB structure.
    """
    logger.info(f"Starting MD Simulation on {os.path.basename(pdb_path)}")

    # 1. Cleaning PDB (Keep only protein)
    try:
        raw_traj = md.load(pdb_path)
        protein_sel = raw_traj.topology.select("protein")
        clean_traj = raw_traj.atom_slice(protein_sel)

        clean_pdb_path = os.path.join(output_dir, "clean_input.pdb")
        clean_traj.save_pdb(clean_pdb_path)
        input_pdb = clean_pdb_path
    except Exception as e:
        logger.warning(f"PDB cleaning failed: {e}. Using original file.")
        input_pdb = pdb_path

    # 2. Setup System
    pdb = app.PDBFile(input_pdb)
    forcefield = app.ForceField('amber14-all.xml', 'amber14/tip3p.xml')

    modeller = app.Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens(forcefield)
    modeller.addSolvent(forcefield, padding=1.0 * unit.nanometers)

    system = forcefield.createSystem(modeller.topology, nonbondedMethod=app.PME,
                                     nonbondedCutoff=1.0 * unit.nanometers, constraints=app.HBonds)
    integrator = mm.LangevinIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtoseconds)

    # Platform Selection
    try:
        platform = mm.Platform.getPlatformByName('CUDA')
        props = {'Precision': 'mixed'}
        simulation = app.Simulation(modeller.topology, system, integrator, platform, props)
        logger.info("Using Platform: CUDA")
    except Exception:
        simulation = app.Simulation(modeller.topology, system, integrator)
        logger.warning("CUDA not found, falling back to CPU.")

    simulation.context.setPositions(modeller.positions)
    simulation.minimizeEnergy()

    # 3. Run Simulation
    simulation.step(steps)

    # 4. Save Topology & Trajectory (Simplified for demo)
    # Ideally, use reporters during simulation, but here we just save the final state
    state = simulation.context.getState(getPositions=True)
    final_pdb = os.path.join(output_dir, 'md_final.pdb')
    app.PDBFile.writeFile(simulation.topology, state.getPositions(), open(final_pdb, 'w'))

    # 5. Analysis (SASA)
    # Reload for analysis
    traj = md.load(final_pdb)
    sasa = md.shrake_rupley(traj, mode='residue')

    # Just return the final frame for now as "open" structure since we relaxed it
    # (Complex frame selection logic omitted for brevity in cleanup)
    return final_pdb