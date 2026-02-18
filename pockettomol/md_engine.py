import os
import mdtraj as md
import numpy as np
import openmm as mm
import openmm.app as app
import openmm.unit as unit
from sys import stdout

def run_simulation_and_pick_open_structure(pdb_path, target_residue_idx, output_dir, steps=10000):
    """
    运行 MD 模拟并挑选目标残基最暴露（口袋最张开）的构象。
    [升级版] 自动清洗 PDB，剔除 SO4、配体等非蛋白原子，防止力场报错。
    """
    print(f"\n--- [MD Engine] Starting Simulation on {os.path.basename(pdb_path)} ---")
    
    # ==========================================
    # 0. 预处理：清洗 PDB (只保留蛋白质)
    # ==========================================
    print("Cleaning PDB structure (removing ions/ligands)...")
    try:
        # 使用 MDTraj 加载原始结构
        raw_traj = md.load(pdb_path)
        
        # 筛选：只保留蛋白质原子
        protein_indices = raw_traj.topology.select("protein")
        
        if len(protein_indices) == 0:
            raise ValueError("No protein atoms found in PDB!")
            
        clean_traj = raw_traj.atom_slice(protein_indices)
        
        # 保存为临时文件
        clean_pdb_path = os.path.join(output_dir, "clean_input.pdb")
        clean_traj.save_pdb(clean_pdb_path)
        print(f"Cleaned PDB saved to: {clean_pdb_path}")
        
        # 更新 pdb_path 指向清洗后的文件
        input_pdb_path = clean_pdb_path
        
    except Exception as e:
        print(f"[Warning] PDB cleaning failed: {e}. Trying original file...")
        input_pdb_path = pdb_path

    # ==========================================
    # 1. 准备拓扑和力场
    # ==========================================
    pdb = app.PDBFile(input_pdb_path)
    forcefield = app.ForceField('amber14-all.xml', 'amber14/tip3p.xml')
    
    # 2. 建模 (添加水盒子)
    modeller = app.Modeller(pdb.topology, pdb.positions)
    print("Adding hydrogens...")
    modeller.addHydrogens(forcefield)
    print("Adding solvent...")
    modeller.addSolvent(forcefield, padding=1.0*unit.nanometers)
    
    print("System solvated. Atoms:", modeller.topology.getNumAtoms())

    # 3. 创建系统
    system = forcefield.createSystem(modeller.topology, nonbondedMethod=app.PME, 
                                     nonbondedCutoff=1.0*unit.nanometers, constraints=app.HBonds)
    
    integrator = mm.LangevinIntegrator(300*unit.kelvin, 1.0/unit.picosecond, 2.0*unit.femtoseconds)
    
    # 尝试使用 CUDA
    try:
        platform = mm.Platform.getPlatformByName('CUDA')
        prop = {'Precision': 'mixed'}
        simulation = app.Simulation(modeller.topology, system, integrator, platform, prop)
        print(f"Using platform: {platform.getName()}")
    except Exception:
        print("CUDA not found. Falling back to CPU.")
        simulation = app.Simulation(modeller.topology, system, integrator)
    
    simulation.context.setPositions(modeller.positions)
    
    # 4. 能量最小化
    print("Minimizing energy...")
    simulation.minimizeEnergy()
    
    # 5. 运行模拟
    print(f"Simulating for {steps} steps...")
    
    dcd_path = os.path.join(output_dir, 'traj.dcd')
    dcd_reporter = app.DCDReporter(dcd_path, 1000) 
    simulation.reporters.append(dcd_reporter)
    # 减少控制台输出频率，避免刷屏
    simulation.reporters.append(app.StateDataReporter(stdout, 2000, step=True, potentialEnergy=True, temperature=True, speed=True))
    
    simulation.step(steps)
    print("Simulation complete.")

    # 6. 保存拓扑
    top_path = os.path.join(output_dir, 'topology.pdb')
    with open(top_path, 'w') as f:
        app.PDBFile.writeFile(simulation.topology, simulation.context.getState(getPositions=True).getPositions(), f)

    # 7. 智能筛选
    print("Analyzing trajectory...")
    traj = md.load(dcd_path, top=top_path)
    
    protein_sel = traj.topology.select("protein")
    traj_prot = traj.atom_slice(protein_sel)
    
    sasa = md.shrake_rupley(traj_prot, mode='residue')
    
    # 映射索引：因为清洗过，残基索引应该和原始 PDB 的蛋白部分基本一致
    if target_residue_idx < sasa.shape[1]:
        target_sasa = sasa[:, target_residue_idx]
        best_frame_idx = np.argmax(target_sasa)
        max_sasa_val = target_sasa[best_frame_idx]
        print(f"Frame {best_frame_idx} has max SASA ({max_sasa_val:.4f}) at residue {target_residue_idx}.")
    else:
        print(f"[Warning] Target residue {target_residue_idx} out of range (max {sasa.shape[1]-1}). Using last frame.")
        best_frame_idx = -1
    
    best_conf_path = os.path.join(output_dir, 'best_open_pocket.pdb')
    traj_prot[best_frame_idx].save_pdb(best_conf_path)
    
    return best_conf_path