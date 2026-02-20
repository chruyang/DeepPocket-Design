import os
import sys
import json
import threading
import traceback
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

try:
    from pipeline.bridge import run_pocketminer, get_residue_center, run_graphbp
    from pipeline import md_engine

    PIPELINE_READY = True
except ImportError as e:
    print(f"[Django Error] Failed to load pipeline: {e}")
    PIPELINE_READY = False


def index(request):
    return render(request, 'index.html')


# ==========================================
# Added: Background computation thread function
# ==========================================
def background_task(file_path, upload_dir, task_id):
    """Execute time-consuming AI pipeline in background and write results to status.json"""
    status_file = os.path.join(upload_dir, 'status.json')
    try:
        print(f"\n--- [Task {task_id}] Started in Background ---")

        # 1. PocketMiner
        target_res_idx = run_pocketminer(file_path)
        if target_res_idx is None:
            raise ValueError("PocketMiner failed to find a pocket.")

        # 2. MD Simulation (You can safely use 5000 steps now)
        print(f"--- [Task {task_id}] Running MD ---")
        md_pdb_path = md_engine.run_simulation(file_path, target_res_idx, upload_dir, steps=5000)

        # 3. GraphBP
        print(f"--- [Task {task_id}] Running GraphBP ---")
        center = get_residue_center(md_pdb_path, target_res_idx)
        run_graphbp(md_pdb_path, center, upload_dir)

        # 4. Update status file after success
        result_url = f"/media/tasks/{task_id}/generated_molecules.pkl"
        pdb_url = f"/media/tasks/{task_id}/md_final.pdb"
        with open(status_file, 'w') as f:
            json.dump({
                'status': 'success',
                'pocket_residue': int(target_res_idx),
                'center': [float(x) for x in center.numpy()],
                'result_url': result_url,
                'pdb_url': pdb_url
            }, f)
        print(f"--- [Task {task_id}] Finished Successfully! ---")

    except Exception as e:
        traceback.print_exc()
        with open(status_file, 'w') as f:
            json.dump({'status': 'error', 'message': str(e)}, f)


# ==========================================
# Modified: API interface changed to asynchronous submission
# ==========================================
@csrf_exempt
def run_pipeline(request):
    if request.method != 'POST': return JsonResponse({'status': 'error'})
    if not PIPELINE_READY: return JsonResponse({'status': 'error', 'message': 'Pipeline not ready'})

    pdb_file = request.FILES.get('pdb_file')
    if not pdb_file: return JsonResponse({'status': 'error', 'message': 'No file'})

    # 创建任务目录
    task_id = os.path.splitext(pdb_file.name)[0]
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'tasks', task_id)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, 'input.pdb')

    with open(file_path, 'wb+') as f:
        for chunk in pdb_file.chunks(): f.write(chunk)

    # 初始化状态为 processing
    status_file = os.path.join(upload_dir, 'status.json')
    with open(status_file, 'w') as f:
        json.dump({'status': 'processing', 'message': 'Task is running in background...'}, f)

    # 启动后台线程执行计算 (这行代码不阻塞，瞬间返回)
    thread = threading.Thread(target=background_task, args=(file_path, upload_dir, task_id))
    thread.start()

    # Instantly respond to frontend, tell frontend the task ID
    return JsonResponse({'status': 'processing', 'task_id': task_id})


# ==========================================
# Added: Query task status interface
# ==========================================
def check_status(request):
    task_id = request.GET.get('task_id')
    if not task_id: return JsonResponse({'status': 'error', 'message': 'Missing task_id'})

    status_file = os.path.join(settings.MEDIA_ROOT, 'tasks', task_id, 'status.json')
    if not os.path.exists(status_file):
        return JsonResponse({'status': 'error', 'message': 'Task not found'})

    with open(status_file, 'r') as f:
        status_data = json.load(f)

    return JsonResponse(status_data)