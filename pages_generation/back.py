#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学诊断打分系统 - 简化版Django后端
功能：
1. GET / -> 返回index.html汇总页面
2. POST /submit -> 接收评分结果并保存CSV
3. GET /<case_id> -> 返回对应病例的评分页面
"""

import os
import sys
import csv
import json
import logging
from datetime import datetime
from pathlib import Path

import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.urls import path, re_path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Django设置
BASE_DIR = Path(__file__).resolve().parent

if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY='medical-scoring-simple-2024',
        ALLOWED_HOSTS=['*'],
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ],
        LANGUAGE_CODE='zh-hans',
        TIME_ZONE='Asia/Shanghai',
        USE_TZ=True,
        CSRF_TRUSTED_ORIGINS=['http://localhost:8124', 'http://127.0.0.1:8124'],
        CSV_STORAGE_DIR=BASE_DIR / 'csv_results',
        PAGES_DIR=BASE_DIR / 'medical_scoring_pages',
    )
    django.setup()

# 确保目录存在
CSV_DIR = settings.CSV_STORAGE_DIR
CSV_DIR.mkdir(exist_ok=True)

PAGES_DIR = settings.PAGES_DIR

def clean_filename(filename):
    """清理文件名"""
    import re
    return re.sub(r'[^\w\-_.]', '_', filename)

@csrf_exempt
def submit_scores(request):
    """接收评分结果的POST接口"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '只支持POST请求'}, status=405)
    
    try:
        # 解析JSON数据
        data = json.loads(request.body)
        
        # 验证必要字段
        required_fields = ['caseId', 'evaluatorName', 'results']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'success': False, 'error': f'缺少字段: {field}'}, status=400)
        
        # 生成CSV文件名
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        case_id = clean_filename(str(data['caseId']))
        evaluator = clean_filename(str(data['evaluatorName']))
        filename = f"{case_id}_{evaluator}_{timestamp}.csv"
        filepath = CSV_DIR / filename
        
        # 保存CSV文件
        fieldnames = ['id', '医师', '辩证症型', '成分与克数', '处方名', '付数', '西医诊断', '医嘱', '用法', '治则', '中医诊断', '评分员', '评分时间']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in data['results']:
                row = {
                    'id': result['id'],
                    '医师': result['doctor'],
                    '辩证症型': result['scores'].get('辩证症型', ''),
                    '成分与克数': result['scores'].get('成分与克数', ''),
                    '处方名': result['scores'].get('处方名', ''),
                    '付数': result['scores'].get('付数', ''),
                    '西医诊断': result['scores'].get('西医诊断', ''),
                    '医嘱': result['scores'].get('医嘱', ''),
                    '用法': result['scores'].get('用法', ''),
                    '治则': result['scores'].get('治则', ''),
                    '中医诊断': result['scores'].get('中医诊断', ''),
                    '评分员': data['evaluatorName'],
                    '评分时间': data.get('timestamp', now.isoformat())
                }
                writer.writerow(row)
        
        logger.info(f"成功保存评分结果: {filename}")
        
        return JsonResponse({
            'success': True,
            'message': '评分结果保存成功',
            'filename': filename
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '无效的JSON数据'}, status=400)
    except Exception as e:
        logger.error(f"保存评分结果失败: {e}")
        return JsonResponse({'success': False, 'error': f'服务器错误: {str(e)}'}, status=500)

def serve_index(request):
    """返回index.html汇总页面"""
    try:
        index_path = PAGES_DIR / 'index.html'
        if not index_path.exists():
            return HttpResponse('index.html文件不存在，请先运行生成脚本', status=404)
        
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return HttpResponse(content, content_type='text/html; charset=utf-8')
    
    except Exception as e:
        logger.error(f"读取index.html失败: {e}")
        return HttpResponse('服务器错误', status=500)

def serve_case_page(request, case_id):
    """返回病例评分页面"""
    try:
        # 直接使用case_id作为文件名
        filename = f"{case_id}"
        case_file = PAGES_DIR / filename
        
        if not case_file.exists():
            return HttpResponse(f'病例页面不存在: {filename}', status=404)
        
        with open(case_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修改前端代码中的API地址为相对路径
        content = content.replace("'/api/save-scores/'", "'/submit'")
        
        return HttpResponse(content, content_type='text/html; charset=utf-8')
    
    except Exception as e:
        logger.error(f"读取病例页面失败: {e}")
        return HttpResponse(f'服务器错误: {str(e)}', status=500)

# URL配置
urlpatterns = [
    path('', serve_index, name='index'),
    path('submit', submit_scores, name='submit'),
    path('<str:case_id>', serve_case_page, name='case_page'),
]

# WSGI应用
application = get_wsgi_application()

def run_server(host='127.0.0.1', port=8124):
    """运行开发服务器"""
    try:
        # 检查必要的目录和文件
        if not PAGES_DIR.exists():
            print(f"❌ 页面目录不存在: {PAGES_DIR}")
            print("请先运行 medical_scoring_generator.py 生成页面")
            return
        
        index_file = PAGES_DIR / 'index.html'
        if not index_file.exists():
            print(f"❌ index.html 不存在: {index_file}")
            print("请先运行 medical_scoring_generator.py 生成页面")
            return
        
        # 检查是否有病例页面
        case_files = list(PAGES_DIR.glob('medical_scoring_*.html'))
        if not case_files:
            print(f"⚠️ 未找到病例页面文件")
            print("请确保 medical_scoring_generator.py 成功生成了页面")
        else:
            print(f"✓ 找到 {len(case_files)} 个病例页面")
        
        from django.core.management import execute_from_command_line
        
        sys.argv = ['manage.py', 'runserver', f'{host}:{port}', '--noreload']
        
        print("🏥 医学诊断打分系统 - 简化版后端")
        print("=" * 45)
        print(f"🌐 汇总页面: http://{host}:{port}/")
        print(f"📤 提交接口: http://{host}:{port}/submit")
        print(f"📋 病例页面: http://{host}:{port}/<case_id>")
        print(f"📁 CSV存储: {CSV_DIR}")
        print(f"📄 页面目录: {PAGES_DIR}")
        if case_files:
            print("📋 可用病例:")
            for case_file in case_files[:5]:
                # 从文件名提取case_id
                case_id = case_file.stem.replace('medical_scoring_', '')
                print(f"   - http://{host}:{port}/{case_id}")
            if len(case_files) > 5:
                print(f"   ... 还有 {len(case_files) - 5} 个病例")
        print("=" * 45)
        print("按 Ctrl+C 停止服务器\n")
        
        execute_from_command_line()
        
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='医学诊断打分系统简化版后端')
    parser.add_argument('--host', default='0.0.0.0', help='主机地址')
    parser.add_argument('--port', type=int, default=8124, help='端口号')
    
    args = parser.parse_args()
    run_server(args.host, args.port)