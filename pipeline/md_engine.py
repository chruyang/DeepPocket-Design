import os
import mdtraj as md
import openmm as mm
import openmm.app as app
import openmm.unit as unit
import logging

# 引入强大的 PDB 修复工具
from pdbfixer import PDBFixer

logger = logging.getLogger(__name__)


def run_simulation(pdb_path, target_res_idx, output_dir, steps=5000):
    """
    Runs a short MD simulation to relax the structure and finding open pocket conformations.
    Includes automated PDB fixing for missing atoms.
    """
    logger.info(f"Starting MD Simulation on {os.path.basename(pdb_path)}")

    # 1. 基础清理 (Keep only protein)
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

    # ==========================================
    # 2. 使用 PDBFixer 自动修补缺失的原子
    # ==========================================
    logger.info("Fixing missing atoms with PDBFixer...")
    fixer = PDBFixer(filename=input_pdb)
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.0)  # 添加 pH=7.0 下的氢原子

    # 保存修复后的 PDB 供 OpenMM 读取
    fixed_pdb_path = os.path.join(output_dir, "fixed_input.pdb")
    with open(fixed_pdb_path, 'w') as f:
        app.PDBFile.writeFile(fixer.topology, fixer.positions, f)

    # ==========================================
    # 3. 设置 OpenMM 系统
    # ==========================================
    pdb = app.PDBFile(fixed_pdb_path)
    forcefield = app.ForceField('amber14-all.xml', 'amber14/tip3p.xml')

    modeller = app.Modeller(pdb.topology, pdb.positions)
    # 因为 PDBFixer 已经加了氢，这里主要加水盒
    modeller.addSolvent(forcefield, padding=1.0 * unit.nanometers)

    system = forcefield.createSystem(modeller.topology, nonbondedMethod=app.PME,
                                     nonbondedCutoff=1.0 * unit.nanometers, constraints=app.HBonds)
    integrator = mm.LangevinIntegrator(300 * unit.kelvin, 1.0 / unit.picosecond, 2.0 * unit.femtoseconds)

    # 平台选择
    try:
        platform = mm.Platform.getPlatformByName('CUDA')
        props = {'Precision': 'mixed'}
        simulation = app.Simulation(modeller.topology, system, integrator, platform, props)
        logger.info("Using Platform: CUDA")
    except Exception:
        simulation = app.Simulation(modeller.topology, system, integrator)
        logger.warning("CUDA not found, falling back to CPU.")

    simulation.context.setPositions(modeller.positions)

    # 能量最小化 (非常重要，消除修复原子带来的空间冲突)
    logger.info("Minimizing energy...")
    simulation.minimizeEnergy()

    # 4. 运行 MD 模拟
    logger.info(f"Running simulation for {steps} steps...")
    simulation.step(steps)

    # 5. 保存结果
    state = simulation.context.getState(getPositions=True)
    final_pdb = os.path.join(output_dir, 'md_final.pdb')
    app.PDBFile.writeFile(simulation.topology, state.getPositions(), open(final_pdb, 'w'))

    return final_pdb