import os
import sys
import json
import threading
import traceback
import pickle
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rdkit import Chem

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# 将 GraphBP 加入环境变量，以便导入 BondAdder
GRAPHBP_PATH = os.path.join(PROJECT_ROOT, 'modules', 'GraphBP', 'GraphBP')
if GRAPHBP_PATH not in sys.path:
    sys.path.append(GRAPHBP_PATH)

try:
    from pipeline.bridge import run_pocketminer, get_residue_center, run_graphbp
    from pipeline import md_engine
    from utils.bond_adding import BondAdder  # 导入成键工具

    PIPELINE_READY = True
except ImportError as e:
    print(f"[Django Error] Failed to load pipeline: {e}")
    PIPELINE_READY = False


def index(request):
    return render(request, 'index.html')


# ==========================================
# 新增：格式转换函数 (PKL -> SDF)
# ==========================================
def convert_pkl_to_sdf(pkl_path, sdf_path):
    """读取已经过滤好的纯有机 pkl，重构化学键并保存为标准 sdf"""
    with open(pkl_path, 'rb') as f:
        mol_dicts = pickle.load(f)

    bond_adder = BondAdder()
    writer = Chem.SDWriter(sdf_path)
    success_count = 0

    for key, data in mol_dicts.items():
        if not isinstance(key, int):
            continue

        num_atom = key
        atomic_numbers_batch = data['_atomic_numbers']
        positions_batch = data['_positions']
        num_mols_in_batch = len(atomic_numbers_batch)

        for i in range(num_mols_in_batch):
            atomic_numbers = atomic_numbers_batch[i]
            positions = positions_batch[i]
            try:
                rd_mol, _ = bond_adder.make_mol(atomic_numbers, positions)
                if rd_mol is not None:
                    rd_mol.SetProp("_Name", f"AI_Organic_Mol_{success_count + 1}")
                    writer.write(rd_mol)
                    success_count += 1
            except Exception:
                pass

    writer.close()
    return success_count


# ==========================================
# 后台计算线程函数
# ==========================================
def background_task(file_path, upload_dir, task_id):
    status_file = os.path.join(upload_dir, 'status.json')
    try:
        print(f"\n--- [Task {task_id}] Started in Background ---")

        # 1. PocketMiner
        target_res_idx = run_pocketminer(file_path)
        if target_res_idx is None:
            raise ValueError("PocketMiner failed to find a pocket.")

        # 2. MD Simulation
        print(f"--- [Task {task_id}] Running MD ---")
        md_pdb_path = md_engine.run_simulation(file_path, target_res_idx, upload_dir, steps=5000)

        # 3. GraphBP (固定生成 10 个)
        print(f"--- [Task {task_id}] Running GraphBP ---")
        center = get_residue_center(md_pdb_path, target_res_idx)
        run_graphbp(md_pdb_path, center, upload_dir)

        # 4. 转换为 SDF
        print(f"--- [Task {task_id}] Converting to SDF ---")
        pkl_file = os.path.join(upload_dir, 'generated_molecules.pkl')
        sdf_file = os.path.join(upload_dir, 'generated_molecules.sdf')

        num_organic_mols = convert_pkl_to_sdf(pkl_file, sdf_file)
        print(f"--- [Task {task_id}] Successfully generated {num_organic_mols} organic molecules in SDF! ---")

        # 5. 成功后更新状态文件
        result_url = f"/media/tasks/{task_id}/generated_molecules.sdf"
        pdb_url = f"/media/tasks/{task_id}/md_final.pdb"

        with open(status_file, 'w') as f:
            json.dump({
                'status': 'success',
                'pocket_residue': int(target_res_idx),
                'center': [float(x) for x in center.numpy()],
                'result_url': result_url,
                'pdb_url': pdb_url,
                'num_mols': num_organic_mols
            }, f)
        print(f"--- [Task {task_id}] Finished Successfully! ---")

    except Exception as e:
        traceback.print_exc()
        with open(status_file, 'w') as f:
            json.dump({'status': 'error', 'message': str(e)}, f)


# ==========================================
# API 接口逻辑
# ==========================================
@csrf_exempt
def run_pipeline(request):
    if request.method != 'POST': return JsonResponse({'status': 'error'})
    if not PIPELINE_READY: return JsonResponse({'status': 'error', 'message': 'Pipeline not ready'})

    pdb_file = request.FILES.get('pdb_file')
    if not pdb_file: return JsonResponse({'status': 'error', 'message': 'No file'})

    task_id = os.path.splitext(pdb_file.name)[0]
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'tasks', task_id)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, 'input.pdb')

    with open(file_path, 'wb+') as f:
        for chunk in pdb_file.chunks(): f.write(chunk)

    status_file = os.path.join(upload_dir, 'status.json')
    with open(status_file, 'w') as f:
        json.dump({'status': 'processing', 'message': 'Task is running...'}, f)

    thread = threading.Thread(target=background_task, args=(file_path, upload_dir, task_id))
    thread.start()

    return JsonResponse({'status': 'processing', 'task_id': task_id})


def check_status(request):
    task_id = request.GET.get('task_id')
    if not task_id: return JsonResponse({'status': 'error', 'message': 'Missing task_id'})
    status_file = os.path.join(settings.MEDIA_ROOT, 'tasks', task_id, 'status.json')
    if not os.path.exists(status_file):
        return JsonResponse({'status': 'error', 'message': 'Task not found'})
    with open(status_file, 'r') as f:
        status_data = json.load(f)
    return JsonResponse(status_data)