import os
import openmm as mm
import openmm.app as app
import openmm.unit as unit
import logging
from pdbfixer import PDBFixer

logger = logging.getLogger(__name__)


def run_simulation(pdb_path, target_res_idx, output_dir, steps=5000):
    """
    Runs MD simulation with pure-text pre/post processing to strictly preserve
    original PDB residue numbering.
    """
    logger.info(f"Starting MD Simulation on {os.path.basename(pdb_path)}")

    # ==========================================
    # 1. 基础清理：纯文本过滤 (完全保留原有残基序号)
    # ==========================================
    clean_pdb_path = os.path.join(output_dir, "clean_input.pdb")
    valid_res = {"ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS",
                 "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP",
                 "TYR", "VAL", "CYX", "HID", "HIE", "HIP"}

    try:
        with open(pdb_path, 'r') as fin, open(clean_pdb_path, 'w') as fout:
            for line in fin:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    res_name = line[17:20].strip()
                    if res_name in valid_res:
                        fout.write(line)
                elif line.startswith(("CRYST1", "END", "TER")):
                    fout.write(line)
        input_pdb = clean_pdb_path
    except Exception as e:
        logger.warning(f"PDB cleaning failed: {e}. Using original file.")
        input_pdb = pdb_path

    # ==========================================
    # 2. 自动修补与设置系统
    # ==========================================
    logger.info("Fixing missing atoms with PDBFixer...")
    fixer = PDBFixer(filename=input_pdb)
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)

    fixed_pdb_path = os.path.join(output_dir, "fixed_input.pdb")
    with open(fixed_pdb_path, 'w') as f:
        # 【关键】keepIds=True 强制 OpenMM 保留修复前的残基序号
        app.PDBFile.writeFile(fixer.topology, fixer.positions, f, keepIds=True)

    pdb = app.PDBFile(fixed_pdb_path)
    forcefield = app.ForceField('amber14-all.xml', 'amber14/tip3p.xml')

    modeller = app.Modeller(pdb.topology, pdb.positions)
    modeller.addSolvent(forcefield, padding=1.0 * unit.nanometers)

    system = forcefield.createSystem(modeller.topology, nonbondedMethod=app.PME,
                                     nonbondedCutoff=1.0 * unit.nanometers, constraints=app.HBonds)
    integrator = mm.LangevinIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtoseconds)

    try:
        platform = mm.Platform.getPlatformByName('CUDA')
        props = {'Precision': 'mixed'}
        simulation = app.Simulation(modeller.topology, system, integrator, platform, props)
        logger.info("Using Platform: CUDA")
    except Exception:
        simulation = app.Simulation(modeller.topology, system, integrator)
        logger.warning("CUDA not found, falling back to CPU.")

    simulation.context.setPositions(modeller.positions)
    logger.info("Minimizing energy...")
    simulation.minimizeEnergy()
    logger.info(f"Running simulation for {steps} steps...")
    simulation.step(steps)

    # ==========================================
    # 3. 保存并进行纯文本脱水
    # ==========================================
    state = simulation.context.getState(getPositions=True)
    raw_final_pdb = os.path.join(output_dir, 'md_raw_with_water.pdb')
    with open(raw_final_pdb, 'w') as f:
        # 再次强制保留 IDs
        app.PDBFile.writeFile(simulation.topology, state.getPositions(), f, keepIds=True)

    final_pdb = os.path.join(output_dir, 'md_final.pdb')
    try:
        logger.info("Stripping solvent via text parsing...")
        with open(raw_final_pdb, 'r') as fin, open(final_pdb, 'w') as fout:
            for line in fin:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    res_name = line[17:20].strip()
                    # 剔除水分子的名称标识
                    if res_name not in ["HOH", "WAT", "Na+", "Cl-", "NA", "CL"]:
                        fout.write(line)
                elif line.startswith(("CRYST1", "END", "TER")):
                    fout.write(line)
    except Exception as e:
        logger.error(f"Solvent stripping failed: {e}")
        final_pdb = raw_final_pdb

    return final_pdb