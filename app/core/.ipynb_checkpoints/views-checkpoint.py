import os
import sys
import traceback
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ==========================================
# 1. 引入同级目录下的计算管线
# ==========================================
# 获取项目根目录 (pockettomol)
BASE_DIR = settings.BASE_DIR
sys.path.append(str(BASE_DIR))

try:
    # 直接导入根目录下的脚本
    from pipeline.bridge import run_pocketminer_logic, get_residue_center_from_pdb, run_graphbp_logic
    from pipeline import md_engine

    PIPELINE_READY = True
    print("[Django] Pipeline modules loaded successfully.")
except ImportError as e:
    PIPELINE_READY = False
    print(f"[Django Error] Failed to load pipeline: {e}")

# ==========================================
# 2. 视图函数
# ==========================================

def index(request):
    """渲染主页"""
    return render(request, 'index.html')

@csrf_exempt  # 暂时禁用 CSRF 方便测试
def run_pipeline(request):
    """核心接口：接收 PDB -> 运行 AI -> 返回结果"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'})
    
    if 'pdb_file' not in request.FILES:
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'})

    if not PIPELINE_READY:
        return JsonResponse({'status': 'error', 'message': 'Backend pipeline not initialized'})

    try:
        # A. 保存上传文件
        pdb_file = request.FILES['pdb_file']
        
        # 创建本次任务的专属目录 (建议用 UUID，这里演示简单起见直接用文件名)
        task_id = os.path.splitext(pdb_file.name)[0]
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'tasks', task_id)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        file_path = os.path.join(upload_dir, 'input.pdb')
        
        # 写入文件
        with open(file_path, 'wb+') as f:
            for chunk in pdb_file.chunks():
                f.write(chunk)
        
        print(f"--- [Task {task_id}] Started ---")

        # B. 运行 PocketMiner
        target_res_idx = run_pocketminer_logic(file_path)
        if target_res_idx is None:
            return JsonResponse({'status': 'error', 'message': 'PocketMiner failed'})

        # C. 运行 MD (由于您有显卡，我们默认开启)
        md_pdb_path = file_path
        md_status = "Skipped"
        
        try:
            # 运行 5000 步 (约 10ps)，显卡几秒搞定
            print(f"--- [Task {task_id}] Running MD ---")
            md_pdb_path = md_engine.run_simulation_and_pick_open_structure(
                file_path, target_res_idx, upload_dir, steps=5000
            )
            md_status = "Success (GPU)"
        except Exception as e:
            print(f"MD Failed: {e}")
            md_status = f"Failed: {str(e)}"

        # D. 运行 GraphBP
        print(f"--- [Task {task_id}] Running GraphBP ---")
        center = get_residue_center_from_pdb(md_pdb_path, target_res_idx)
        run_graphbp_logic(md_pdb_path, center, upload_dir)

        # E. 检查结果
        result_pkl = os.path.join(upload_dir, 'generated_molecules.pkl')
        if os.path.exists(result_pkl):
            # 构造下载链接
            result_url = f"/media/tasks/{task_id}/generated_molecules.pkl"
            pdb_url = f"/media/tasks/{task_id}/best_open_pocket.pdb" if md_status.startswith("Success") else f"/media/tasks/{task_id}/input.pdb"
            
            return JsonResponse({
                'status': 'success',
                'pocket_residue': int(target_res_idx),
                'md_status': md_status,
                'center': [float(x) for x in center.numpy()],
                'result_url': result_url,
                'pdb_url': pdb_url
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'GraphBP generation failed'})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)})