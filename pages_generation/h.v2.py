# -*- coding: utf-8 -*-
"""
医学诊断打分系统 - 批量网页生成器
从CSV文件读取数据并生成对应的HTML评分页面
"""

import pandas as pd
import json
import os
from datetime import datetime
import re

def clean_filename(filename):
    """清理文件名，移除不合法字符"""
    return re.sub(r'[^\w\-_.]', '_', filename)

def format_case_info(case_info_text):
    """
    格式化病例信息，以冒号为分隔符解析各个字段
    """
    if not case_info_text or pd.isna(case_info_text):
        return '<p>病例信息缺失</p>'
    
    # 定义字段名列表，按照常见顺序
    field_names = ['性别', '年龄', '职业', '初诊日期', '主诉', '现病史', '刻诊', '专科检查', '辅助检查']
    
    # 先规范化文本，在字段名前添加分隔符（除了第一个）
    normalized_text = case_info_text
    for field in field_names[1:]:  # 跳过第一个字段
        # 在字段名前添加 | 作为分隔符，但要避免重复添加
        normalized_text = normalized_text.replace(f'{field}：', f'|{field}：')
    
    # 按 | 分割
    segments = normalized_text.split('|')
    
    # 解析每个段落
    parsed_info = {}
    
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
            
        # 查找冒号
        colon_pos = segment.find('：')
        if colon_pos == -1:
            continue
            
        # 提取字段名和内容
        field_name = segment[:colon_pos].strip()
        field_content = segment[colon_pos+1:].strip()
        
        # 检查是否是我们关注的字段
        if field_name in field_names:
            parsed_info[field_name] = field_content
    
    # 如果解析失败，返回原始文本
    if not parsed_info:
        return f'<p><strong>病例信息：</strong>{case_info_text}</p>'
    
    # 生成HTML格式
    html_parts = []
    
    # 基本信息行（性别、年龄、职业、初诊日期）
    basic_fields = ['性别', '年龄', '职业', '初诊日期']
    basic_info_parts = []
    
    for field in basic_fields:
        if field in parsed_info:
            if field == '初诊日期':
                basic_info_parts.append(f"初诊日期：{parsed_info[field]}")
            else:
                basic_info_parts.append(parsed_info[field])
    
    if basic_info_parts:
        # 前三个信息组成患者信息
        patient_parts = basic_info_parts[:3]
        patient_info = f"<p><strong>患者：</strong>{', '.join(patient_parts)}"
        
        # 如果有初诊日期，单独显示
        if len(basic_info_parts) > 3:
            patient_info += f" &nbsp; <strong>{basic_info_parts[3]}</strong>"
        
        patient_info += "</p>"
        html_parts.append(patient_info)
    
    # 详细信息（按顺序显示）
    detail_fields = ['主诉', '现病史', '刻诊', '专科检查', '辅助检查']
    
    for field in detail_fields:
        if field in parsed_info and parsed_info[field]:
            html_parts.append(f"<p><strong>{field}：</strong>{parsed_info[field]}</p>")
    
    return '\n            '.join(html_parts)

def generate_field_tabs(fields):
    """生成字段标签"""
    tabs_html = ""
    for i, field in enumerate(fields):
        active_class = "active" if i == 0 else ""
        tabs_html += f'<button class="tab-button {active_class}" data-field="{field}">{field}</button>\n            '
    return tabs_html.strip()

def generate_html_template(case_data, case_id):
    print(f"    ✓ 进入HTML模板生成函数")
    print(f"    ✓ 参数检查 - case_id: {case_id}")
    print(f"    ✓ 参数检查 - case_data类型: {type(case_data)}")
    
    try:
        # 基本数据检查
        if case_data.empty:
            raise ValueError(f"病例 {case_id} 的数据为空")
        
        doctor_count = len(case_data)
        print(f"    ✓ 医师数量: {doctor_count}")
        
        # 提取病例信息
        case_info = case_data.iloc[0]['题目'] if '题目' in case_data.columns else "病例信息缺失"
        print(f"    ✓ 病例信息提取成功")
        
        # 格式化病例信息
        formatted_case_info = format_case_info(case_info)
        print(f"    ✓ 病例信息格式化完成")
        
        # 准备医师数据
        fields = ['中医诊断', '辩证症型', '西医诊断', '治则', '处方名', '成分与克数', '付数', '用法', '医嘱']
        medical_data = {"caseId": str(case_id)}
        
        # 提取各字段数据
        for field in fields:
            if field in case_data.columns:
                field_data = [str(x) if not pd.isna(x) else '数据缺失' for x in case_data[field].tolist()]
            else:
                field_data = ['字段缺失'] * doctor_count
            medical_data[field] = field_data
        
        # 提取真实医师名称（用于导出）
        if '医师' in case_data.columns:
            real_doctor_names = [str(x) if not pd.isna(x) else f'医师{i+1}' for i, x in enumerate(case_data['医师'].tolist())]
        else:
            real_doctor_names = [f'医师{i+1}' for i in range(doctor_count)]
        
        # 生成匿名化医师名称（用于显示）
        display_doctor_names = [f'医师{i+1}' for i in range(doctor_count)]
        
        print(f"    ✓ 数据组织完成")
        print(f"    ✓ 真实医师: {real_doctor_names}")
        print(f"    ✓ 显示医师: {display_doctor_names}")
        
        # 生成字段标签
        field_tabs = generate_field_tabs(fields)
        
        # 序列化数据
        medical_data_json = json.dumps(medical_data, ensure_ascii=False, indent=2)
        display_doctor_names_json = json.dumps(display_doctor_names, ensure_ascii=False)
        real_doctor_names_json = json.dumps(real_doctor_names, ensure_ascii=False)
        
        print(f"    ✓ 开始生成HTML...")
        
        # HTML模板
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>医学诊断打分系统 - {case_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #2c5aa0 0%, #1e3a8a 50%, #164e63 100%); min-height: 100vh; padding: 10px; }}
        .container {{ max-width: 1600px; margin: 0 auto; background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 20px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15); }}
        .header {{ text-align: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 3px solid #2c5aa0; }}
        .header h1 {{ color: #1e3a8a; font-size: 2em; margin-bottom: 10px; }}
        .evaluator-section {{ background: linear-gradient(135deg, #fef7ff, #f3e8ff); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid #8b5cf6; }}
        .evaluator-section h3 {{ color: #8b5cf6; margin-bottom: 15px; font-size: 1.2em; }}
        .input-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .input-group label {{ font-weight: 600; color: #555; }}
        .required {{ color: #dc2626; font-weight: bold; }}
        .input-group input {{ padding: 12px 15px; border: 2px solid #e2e8f0; border-radius: 8px; font-size: 1em; width: 100%; max-width: 400px; }}
        .input-note {{ font-size: 0.85em; color: #666; font-style: italic; }}
        .case-id-section {{ background: linear-gradient(135deg, #f0fdfa, #e6fffa); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 2px solid #14b8a6; }}
        .case-id-section h3 {{ color: #14b8a6; margin-bottom: 15px; font-size: 1.2em; }}
        .case-id-display {{ padding: 12px 15px; border: 2px solid #14b8a6; border-radius: 8px; font-size: 1.1em; font-weight: 600; color: #14b8a6; background: #f0fdfa; width: 100%; max-width: 400px; font-family: 'Courier New', monospace; word-break: break-all; }}
        .case-info {{ background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border-radius: 12px; padding: 20px; margin-bottom: 20px; border-left: 5px solid #0891b2; }}
        .case-info h3 {{ color: #0891b2; margin-bottom: 10px; font-size: 1.2em; }}
        .case-info p {{ color: #555; line-height: 1.6; font-size: 0.9em; margin-bottom: 8px; }}
        .progress-section {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 15px; margin-bottom: 20px; padding: 20px; background: linear-gradient(135deg, #f8fafc, #e2e8f0); border-radius: 12px; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 1.8em; font-weight: bold; color: #1e3a8a; }}
        .stat-label {{ color: #666; margin-top: 5px; font-size: 0.85em; }}
        .progress-bar {{ width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; margin-bottom: 20px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #0891b2, #1e3a8a); width: 0%; transition: width 0.3s ease; }}
        .field-tabs {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 8px; margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 12px; }}
        .tab-button {{ padding: 10px 8px; background: white; border: 2px solid #e2e8f0; cursor: pointer; font-size: 0.8em; font-weight: 600; color: #666; border-radius: 8px; text-align: center; transition: all 0.3s ease; }}
        .tab-button:hover {{ border-color: #0891b2; color: #0891b2; }}
        .tab-button.active {{ background: linear-gradient(135deg, #0891b2, #1e3a8a); color: white; border-color: #0891b2; }}
        .doctor-row {{ display: flex; flex-direction: column; padding: 20px; margin-bottom: 15px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); border-left: 4px solid #0891b2; }}
        .doctor-info {{ font-weight: 600; color: #1e3a8a; font-size: 1.1em; text-align: center; padding: 10px; background: #f0f9ff; border-radius: 8px; margin-bottom: 15px; }}
        .doctor-answer {{ padding: 15px; background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; line-height: 1.6; color: #444; margin-bottom: 15px; min-height: 80px; word-wrap: break-word; }}
        .prescription-text {{ font-family: 'Courier New', monospace; background: #f0fdf4 !important; border: 1px solid #22c55e !important; }}
        .rating-section {{ display: flex; flex-direction: column; align-items: center; }}
        .rating-label {{ margin-bottom: 10px; font-weight: 600; color: #555; text-align: center; font-size: 0.95em; }}
        .rating-buttons {{ display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; justify-content: center; }}
        .rating-button {{ width: 45px; height: 45px; border: 3px solid #e2e8f0; background: white; border-radius: 50%; cursor: pointer; font-weight: bold; font-size: 1.1em; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease; }}
        .rating-button:hover {{ transform: scale(1.05); }}
        .rating-button.selected {{ background: linear-gradient(135deg, #0891b2, #1e3a8a); color: white; border-color: #0891b2; }}
        .rating-button[data-score="1"] {{ border-color: #dc2626; }}
        .rating-button[data-score="2"] {{ border-color: #ea580c; }}
        .rating-button[data-score="3"] {{ border-color: #d97706; }}
        .rating-button[data-score="4"] {{ border-color: #059669; }}
        .rating-button[data-score="5"] {{ border-color: #047857; }}
        .rating-button[data-score="1"].selected {{ background: #dc2626; border-color: #dc2626; }}
        .rating-button[data-score="2"].selected {{ background: #ea580c; border-color: #ea580c; }}
        .rating-button[data-score="3"].selected {{ background: #d97706; border-color: #d97706; }}
        .rating-button[data-score="4"].selected {{ background: #059669; border-color: #059669; }}
        .rating-button[data-score="5"].selected {{ background: #047857; border-color: #047857; }}
        .score-indicator {{ font-size: 0.75em; color: #666; text-align: center; margin-top: 5px; }}
        .submit-section {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #e2e8f0; }}
        .submit-button {{ background: linear-gradient(135deg, #047857, #059669); color: white; border: none; padding: 15px 30px; border-radius: 50px; font-size: 1.1em; font-weight: 600; cursor: pointer; width: 100%; max-width: 300px; transition: all 0.3s ease; }}
        .submit-button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(4, 120, 87, 0.3); }}
        .alert {{ padding: 15px; margin-bottom: 20px; border-radius: 8px; text-align: center; font-weight: 600; }}
        .alert-success {{ background: #d1fae5; color: #047857; border: 1px solid #059669; }}
        .alert-warning {{ background: #fef3c7; color: #92400e; border: 1px solid #d97706; }}
        .privacy-note {{ background: #fef7cd; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
        .privacy-note h4 {{ color: #92400e; margin-bottom: 8px; font-size: 1em; }}
        .privacy-note p {{ color: #92400e; font-size: 0.85em; margin: 0; }}

        /* 移动端适配 */
        @media (max-width: 768px) {{
            body {{ padding: 5px; }}
            .container {{ padding: 15px; border-radius: 15px; }}
            .header h1 {{ font-size: 1.6em; }}
            .evaluator-section, .case-id-section, .case-info {{ padding: 15px; margin-bottom: 15px; }}
            .evaluator-section h3, .case-id-section h3, .case-info h3 {{ font-size: 1.1em; }}
            .progress-section {{ padding: 15px; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 10px; }}
            .stat-number {{ font-size: 1.5em; }}
            .stat-label {{ font-size: 0.8em; }}
            .field-tabs {{ grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 6px; padding: 10px; }}
            .tab-button {{ padding: 8px 6px; font-size: 0.75em; }}
            .doctor-row {{ padding: 15px; }}
            .doctor-info {{ font-size: 1em; margin-bottom: 12px; }}
            .doctor-answer {{ padding: 12px; margin-bottom: 12px; font-size: 0.9em; }}
            .rating-buttons {{ gap: 4px; }}
            .rating-button {{ width: 40px; height: 40px; font-size: 1em; }}
            .rating-label {{ font-size: 0.9em; }}
            .score-indicator {{ font-size: 0.7em; }}
            .submit-button {{ padding: 12px 25px; font-size: 1em; }}
            .case-info p {{ font-size: 0.85em; }}
            .input-group input {{ font-size: 16px; /* 防止iOS缩放 */ }}
        }}

        @media (max-width: 480px) {{
            .header h1 {{ font-size: 1.4em; }}
            .field-tabs {{ grid-template-columns: repeat(2, 1fr); }}
            .tab-button {{ font-size: 0.7em; padding: 6px 4px; }}
            .progress-section {{ grid-template-columns: repeat(3, 1fr); }}
            .rating-buttons {{ gap: 3px; }}
            .rating-button {{ width: 35px; height: 35px; font-size: 0.9em; }}
            .doctor-answer {{ font-size: 0.85em; }}
            .case-info p {{ font-size: 0.8em; }}
            .privacy-note {{ padding: 12px; }}
            .privacy-note h4 {{ font-size: 0.95em; }}
            .privacy-note p {{ font-size: 0.8em; }}
        }}

        /* 桌面端适配 */
        @media (min-width: 1200px) {{
            .container {{ padding: 30px; }}
            .doctor-row {{ flex-direction: row; align-items: flex-start; }}
            .doctor-info {{ flex: 0 0 120px; margin-right: 20px; margin-bottom: 0; }}
            .doctor-answer {{ flex: 1; margin-right: 20px; margin-bottom: 0; }}
            .rating-section {{ flex: 0 0 320px; }}
            .rating-buttons {{ gap: 8px; }}
            .rating-button {{ width: 50px; height: 50px; font-size: 1.2em; }}
        }}
        
        /* Button base style */
        #goTopBtn {{
          position: fixed;
          bottom: 30px;
          right: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
          width: 48px;
          height: 48px;
          background-color: #1e1e1e;
          color: white;
          font-size: 24px;
          border: none;
          border-radius: 50%;
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
          cursor: pointer;
          opacity: 0;
          visibility: hidden;
          transition: opacity 0.3s ease, transform 0.3s ease;
          z-index: 1000;
        }}

        /* Hover effect */
        #goTopBtn:hover {{
          transform: translateY(-4px);
          background-color: #333;
        }}

        /* Show button */
        #goTopBtn.show {{
          opacity: 1;
          visibility: visible;
        }}

    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 医学诊断打分系统</h1>
        </div>

        <div class="privacy-note">
            <h3>🔒 已打分项目会自动保存，若一次填不完可放心退出。（需在浏览器中打开页面）</h3>
        </div>

        <div class="evaluator-section">
            <h3>📝 评分员信息</h3>
            <div class="input-group">
                <label for="evaluatorName">评分员姓名 <span class="required">*</span></label>
                <input type="text" id="evaluatorName" placeholder="请输入您的姓名" maxlength="20" required>
                <div class="input-note">此信息将记录在评分报告中，请输入真实姓名</div>
            </div>
        </div>

        <div class="case-id-section">
            <h3>🆔 病例标识</h3>
            <div class="info-display">
                <div class="case-id-display" id="caseIdDisplay">{case_id}</div>
            </div>
        </div>

        <div class="case-info">
            <h3>📋 病例信息</h3>
            {formatted_case_info}
        </div>

        <div class="progress-section">
            <div class="stat-item">
                <div class="stat-number" id="totalScored">0</div>
                <div class="stat-label">已评分</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="totalRemaining">{len(fields) * doctor_count}</div>
                <div class="stat-label">待评分</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="currentProgress">0%</div>
                <div class="stat-label">完成度</div>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>

        <div class="field-tabs">
            {field_tabs}
        </div>

        <div id="fieldContainer"></div>

        <button id="goTopBtn"> ⮝ </button>

        <div class="submit-section">
            <div id="alertContainer"></div>
            <button class="submit-button" id="submitBtn" onclick="exportToCSV()">
                📤 提交
            </button>
        </div>
    </div>

    <script>
    
        const goTopBtn = document.getElementById("goTopBtn");

        window.addEventListener("scroll", () => {{
          if (window.scrollY > 300) {{
            goTopBtn.classList.add("show");
          }} else {{
            goTopBtn.classList.remove("show");
          }}
        }});

        goTopBtn.addEventListener("click", () => {{
          window.scrollTo({{
            top: 0,
            behavior: "smooth"
          }});
        }});


    
    
    
    
    
        const medicalData = {medical_data_json};
        const displayDoctorNames = {display_doctor_names_json};  // 用于网页显示的匿名化名称
        const realDoctorNames = {real_doctor_names_json};        // 用于CSV导出的真实名称
        const scores = {{}};
        const fields = Object.keys(medicalData).filter(key => key !== 'caseId');
        const doctorCount = {doctor_count};
        let currentField = fields[0] || '辩证症型';

        function initializeScores() {{
            fields.forEach(field => {{
                scores[field] = {{}};
                for (let i = 1; i <= doctorCount; i++) {{
                    scores[field][i] = null;
                }}
            }});
        }}

        function generateFieldContent() {{
            const container = document.getElementById('fieldContainer');
            if (!container) return;
            
            container.innerHTML = '';
            const fieldDiv = document.createElement('div');
            fieldDiv.className = 'field-content active';
            
            const titleDiv = document.createElement('div');
            titleDiv.style.cssText = 'font-size: 1.4em; font-weight: bold; color: #1e3a8a; margin-bottom: 20px; text-align: center; padding: 15px; background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border-radius: 10px; border: 2px solid #0891b2;';
            titleDiv.textContent = `📋 ${{currentField}} 评分`;
            fieldDiv.appendChild(titleDiv);
            
            if (!medicalData[currentField]) return;
            
            for (let i = 1; i <= doctorCount; i++) {{
                const row = document.createElement('div');
                row.className = 'doctor-row';
                const doctorAnswer = medicalData[currentField][i-1] || '数据缺失';
                const doctorDisplayName = displayDoctorNames[i-1] || `医师${{i}}`;  // 使用匿名化名称显示
                const answerClass = currentField === '成分与克数' ? 'doctor-answer prescription-text' : 'doctor-answer';
                
                row.innerHTML = `
                    <div class="doctor-info">${{doctorDisplayName}}</div>
                    <div class="${{answerClass}}">${{doctorAnswer}}</div>
                    <div class="rating-section">
                        <div class="rating-label">专业评分 (1-5分)</div>
                        <div class="rating-buttons">
                            ${{[1,2,3,4,5].map(score => 
                                `<button class="rating-button ${{scores[currentField][i] === score ? 'selected' : ''}}" 
                                         data-field="${{currentField}}" data-doctor="${{i}}" data-score="${{score}}" 
                                         onclick="setRating('${{currentField}}', ${{i}}, ${{score}})">${{score}}</button>`
                            ).join('')}}
                        </div>
                        <div class="score-indicator">1=差 2=较差 3=一般 4=良好 5=优秀</div>
                    </div>
                `;
                fieldDiv.appendChild(row);
            }}
            container.appendChild(fieldDiv);
        }}

        function setRating(field, doctor, score) {{
            scores[field][doctor] = score;
            const buttons = document.querySelectorAll(`[data-field="${{field}}"][data-doctor="${{doctor}}"]`);
            buttons.forEach(btn => btn.classList.remove('selected'));
            const selectedButton = document.querySelector(`[data-field="${{field}}"][data-doctor="${{doctor}}"][data-score="${{score}}"]`);
            if (selectedButton) selectedButton.classList.add('selected');
            updateProgress();
        }}

        function updateProgress() {{
            let totalScored = 0;
            const totalQuestions = fields.length * doctorCount;
            fields.forEach(field => {{
                for (let i = 1; i <= doctorCount; i++) {{
                    if (scores[field][i] !== null) totalScored++;
                }}
            }});
            const progress = (totalScored / totalQuestions) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('totalScored').textContent = totalScored;
            document.getElementById('totalRemaining').textContent = totalQuestions - totalScored;
            document.getElementById('currentProgress').textContent = Math.round(progress) + '%';
        }}

        function showField(field) {{
            currentField = field;
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            const activeButton = document.querySelector(`[data-field="${{field}}"]`);
            if (activeButton) activeButton.classList.add('active');
            generateFieldContent();
        }}

        function initializeTabButtons() {{
            document.querySelectorAll('.tab-button').forEach(button => {{
                button.addEventListener('click', function() {{
                    const field = this.getAttribute('data-field');
                    showField(field);
                }});
            }});
        }}

        function getEvaluatorName() {{
            const nameInput = document.getElementById('evaluatorName');
            const name = nameInput.value.trim();
            if (!name) {{
                nameInput.focus();
                nameInput.style.borderColor = '#dc2626';
                showAlert('⚠️ 请先输入评分员姓名才能导出报告！', 'warning');
                return null;
            }}
            nameInput.style.borderColor = '#059669';
            return name;
        }}

        function showAlert(message, type = 'success') {{
            const alertContainer = document.getElementById('alertContainer');
            alertContainer.innerHTML = `<div class="alert alert-${{type}}">${{message}}</div>`;
            setTimeout(() => alertContainer.innerHTML = '', 5000);
        }}

        // 缓存相关函数
        function getCacheKey() {{
            return `medical_scoring_${{medicalData.caseId}}`;
        }}

        function saveScoresToCache() {{
            try {{
                const cacheData = {{
                    scores: scores,
                    evaluatorName: document.getElementById('evaluatorName').value.trim(),
                    lastSaved: new Date().toISOString(),
                    caseId: medicalData.caseId
                }};
                localStorage.setItem(getCacheKey(), JSON.stringify(cacheData));
                console.log('评分数据已保存到缓存');
            }} catch (error) {{
                console.warn('保存缓存失败:', error);
            }}
        }}

        function loadScoresFromCache() {{
            try {{
                const cacheKey = getCacheKey();
                const cachedData = localStorage.getItem(cacheKey);
                
                if (cachedData) {{
                    const data = JSON.parse(cachedData);
                    
                    if (data.scores) {{
                        Object.assign(scores, data.scores);
                        console.log('从缓存恢复评分数据:', data.lastSaved);
                    }}
                    
                    if (data.evaluatorName) {{
                        document.getElementById('evaluatorName').value = data.evaluatorName;
                    }}
                    
                    updateAllRatingButtons();
                    updateProgress();
                    
                    if (data.lastSaved) {{
                        const lastSavedTime = new Date(data.lastSaved).toLocaleString('zh-CN');
                        showAlert(`📁 已恢复上次保存的评分数据（${{lastSavedTime}}）`, 'success');
                    }}
                }}
            }} catch (error) {{
                console.warn('加载缓存失败:', error);
            }}
        }}

        function clearScoresCache() {{
            try {{
                localStorage.removeItem(getCacheKey());
                console.log('已清除缓存数据');
            }} catch (error) {{
                console.warn('清除缓存失败:', error);
            }}
        }}

        function updateAllRatingButtons() {{
            fields.forEach(field => {{
                for (let i = 1; i <= doctorCount; i++) {{
                    const score = scores[field][i];
                    if (score !== null) {{
                        const buttons = document.querySelectorAll(`[data-field="${{field}}"][data-doctor="${{i}}"]`);
                        buttons.forEach(btn => btn.classList.remove('selected'));
                        
                        const selectedButton = document.querySelector(`[data-field="${{field}}"][data-doctor="${{i}}"][data-score="${{score}}"]`);
                        if (selectedButton) {{
                            selectedButton.classList.add('selected');
                        }}
                    }}
                }}
            }});
        }}

        // 修改setRating函数，添加自动保存
        function setRating(field, doctor, score) {{
            scores[field][doctor] = score;
            const buttons = document.querySelectorAll(`[data-field="${{field}}"][data-doctor="${{doctor}}"]`);
            buttons.forEach(btn => btn.classList.remove('selected'));
            const selectedButton = document.querySelector(`[data-field="${{field}}"][data-doctor="${{doctor}}"][data-score="${{score}}"]`);
            if (selectedButton) selectedButton.classList.add('selected');
            updateProgress();
            
            // 自动保存到缓存
            saveScoresToCache();
        }}

        function exportToCSV() {{
            const evaluatorName = getEvaluatorName();
            if (!evaluatorName) return;
            
            let totalScored = 0;
            const totalQuestions = fields.length * doctorCount;
            fields.forEach(field => {{
                for (let i = 1; i <= doctorCount; i++) {{
                    if (scores[field][i] !== null) totalScored++;
                }}
            }});
            
            if (totalScored < totalQuestions) {{
                showAlert(`还有 ${{totalQuestions - totalScored}} 个诊断项未评分，请完成所有评分后再导出。`, 'warning');
                return;
            }}
            
            // 准备要发送到服务器的数据
            const exportData = {{
                caseId: medicalData.caseId,
                evaluatorName: evaluatorName,
                timestamp: new Date().toISOString(),
                results: []
            }};
            
            // 构建结果数据 - 使用真实医师姓名
            for (let i = 1; i <= doctorCount; i++) {{
                const result = {{
                    id: medicalData.caseId,
                    doctor: realDoctorNames[i-1],  // 使用真实医师姓名
                    scores: {{}}
                }};
                
                // 添加各字段评分
                fields.forEach(field => {{
                    result.scores[field] = scores[field][i] || '';
                }});
                
                exportData.results.push(result);
            }}
            
            // 显示上传中状态
            const submitBtn = document.getElementById('submitBtn');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = '📤 正在上传到服务器...';
            submitBtn.disabled = true;
            
            // 发送数据到服务器
            fetch('/submit', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()  // Django CSRF保护
                }},
                body: JSON.stringify(exportData)
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error(`服务器错误: ${{response.status}}`);
                }}
                return response.json();
            }})
            .then(data => {{
                if (data.success) {{
                    // 上传成功后清除缓存
                    // clearScoresCache();
                    
                    showAlert(`已保存！`, 'success');
                    
                    // 不再提供下载链接，因为简化版不提供下载接口
                }} else {{
                    throw new Error(data.error || '保存失败');
                }}
            }})
            .catch(error => {{
                console.error('上传错误:', error);
                showAlert(`❌ 保存到服务器失败: ${{error.message}}<br>🔄 请检查网络连接或联系管理员`, 'warning');
                
                // fallback: 如果服务器保存失败，提供本地下载
                setTimeout(() => {{
                    if (confirm('服务器保存失败，是否下载到本地？')) {{
                        downloadCSVLocally(exportData);
                    }}
                }}, 3000);
            }})
            .finally(() => {{
                // 恢复按钮状态
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }});
        }}

        // 获取CSRF Token（Django需要）
        function getCsrfToken() {{
            // 首先尝试从cookie获取
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {{
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {{
                    return value;
                }}
            }}
            
            // 尝试从meta标签获取
            const csrfMeta = document.querySelector('meta[name=csrf-token]');
            if (csrfMeta) {{
                return csrfMeta.getAttribute('content');
            }}
            
            // 如果都没有，返回空字符串（会依赖@csrf_exempt装饰器）
            return '';
        }}

        // 备用本地下载功能
        function downloadCSVLocally(exportData) {{
            const csvRows = [];
            
            // CSV标题行
            const headers = ['id', '医师', '辩证症型', '成分与克数', '处方名', '付数', '西医诊断', '医嘱', '用法', '治则', '中医诊断'];
            csvRows.push(headers.join(','));
            
            // 数据行
            exportData.results.forEach(result => {{
                const row = [
                    result.id,
                    `"${{result.doctor}}"`,  // 加引号避免逗号问题
                    result.scores['辩证症型'] || '',
                    result.scores['成分与克数'] || '',
                    result.scores['处方名'] || '',
                    result.scores['付数'] || '',
                    result.scores['西医诊断'] || '',
                    result.scores['医嘱'] || '',
                    result.scores['用法'] || '',
                    result.scores['治则'] || '',
                    result.scores['中医诊断'] || ''
                ];
                csvRows.push(row.join(','));
            }});
            
            // 创建下载
            const csvContent = csvRows.join('\\n');
            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            
            if (link.download !== undefined) {{
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                
                const now = new Date();
                const dateStr = `${{now.getFullYear()}}-${{(now.getMonth()+1).toString().padStart(2,'0')}}-${{now.getDate().toString().padStart(2,'0')}}`;
                const fileName = `${{exportData.caseId}}-${{exportData.evaluatorName}}-${{dateStr}}.csv`;
                
                link.setAttribute('download', fileName);
                link.style.visibility = 'hidden';
                
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                showAlert(`📁 已下载到本地: ${{fileName}}`, 'success');
            }}
        }}

        // 监听评分员姓名输入，自动保存
        function setupAutoSave() {{
            const nameInput = document.getElementById('evaluatorName');
            nameInput.addEventListener('input', function() {{
                // 延迟保存，避免频繁操作
                clearTimeout(nameInput.saveTimeout);
                nameInput.saveTimeout = setTimeout(saveScoresToCache, 500);
            }});
        }}

        document.addEventListener('DOMContentLoaded', function() {{
            initializeScores();
            initializeTabButtons();
            generateFieldContent();
            
            // 设置自动保存
            setupAutoSave();
            
            // 加载缓存数据（延迟执行，确保页面完全加载）
            setTimeout(() => {{
                loadScoresFromCache();
            }}, 100);
            
            updateProgress();
        }});
    </script>
</body>
</html>"""
        
        print(f"    ✓ HTML生成完成，长度: {len(html_content)} 字符")
        return html_content
        
    except Exception as e:
        print(f"    ❌ HTML生成失败: {e}")
        import traceback
        print(f"    错误详情: {traceback.format_exc()}")
        
        # 返回错误页面
        error_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>错误 - {case_id}</title></head>
<body><h1>病例 {case_id} 处理错误</h1><p>错误: {str(e)}</p></body></html>"""
        return error_html

def process_csv_and_generate_html(csv_file_path, output_dir="output"):
    """处理CSV文件并生成HTML页面"""
    try:
        print(f"正在读取CSV文件: {csv_file_path}")
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        print(f"成功读取数据，共 {len(df)} 行")
        
        # 检查必要的列
        required_columns = ['id', '辩证症型', '成分与克数', '处方名', '付数', '题目', '西医诊断', '医嘱', '用法', '治则', '中医诊断', '医师']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"CSV文件缺少必要的列: {missing_columns}")
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")
        
        # 按病例ID分组
        grouped = df.groupby('id')
        generated_files = []
        
        print(f"发现 {len(grouped)} 个不同的病例ID")
        
        # 处理每个病例
        total_cases = len(grouped)
        current_case = 0
        
        for case_id, case_data in grouped:
            current_case += 1
            print(f"正在处理病例: {case_id} ({current_case}/{total_cases})")
            
            if len(case_data) == 0:
                print(f"警告: 病例 {case_id} 没有数据，跳过")
                continue
            
            try:
                print(f"  - 开始生成HTML内容...")
                print(f"  - case_data类型: {type(case_data)}")
                print(f"  - case_data形状: {case_data.shape}")
                print(f"  - case_id: {case_id}")
                print(f"  - 准备调用HTML模板生成器...")
                
                # 调用HTML生成函数
                html_content = generate_html_template(case_data, case_id)
                print(f"  - HTML内容生成成功，长度: {len(html_content)} 字符")
                
                # 生成文件名并保存
                safe_case_id = clean_filename(str(case_id))
                filename = f"medical_scoring_{safe_case_id}.html"
                filepath = os.path.join(output_dir, filename)
                
                print(f"  - 写入文件: {filename}")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"  - 文件写入成功")
                
                generated_files.append({
                    'case_id': case_id,
                    'filename': filename,
                    'filepath': filepath,
                    'doctor_count': len(case_data)
                })
                
                print(f"✓ 成功生成: {filename} (包含 {len(case_data)} 名医师的诊断)")
                
            except Exception as e:
                print(f"✗ 生成病例 {case_id} 的HTML时出错: {str(e)}")
                import traceback
                print(f"  错误详情: {traceback.format_exc()}")
                continue
        
        # 生成汇总报告
        print("正在生成汇总报告...")
        generate_summary_report(generated_files, output_dir)
        
        print(f"\n🎉 批量生成完成!")
        print(f"📁 输出目录: {os.path.abspath(output_dir)}")
        print(f"📊 成功生成 {len(generated_files)} 个HTML文件")
        print(f"🔒 隐私保护: 网页显示匿名医师编号，CSV导出使用真实姓名")
        
        return generated_files
        
    except Exception as e:
        print(f"❌ 处理过程中发生错误: {str(e)}")
        import traceback
        print(f"完整错误信息:\n{traceback.format_exc()}")
        raise

def generate_summary_report(generated_files, output_dir):
    """生成汇总报告"""
    summary_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>医学诊断打分系统</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; min-height: 100vh; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; padding: 30px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); }}
        .header {{ text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px solid #667eea; }}
        .header h1 {{ color: #333; font-size: 2.5em; margin-bottom: 10px; }}
        .privacy-banner {{ background: #fef7cd; border: 2px solid #f59e0b; border-radius: 12px; padding: 20px; margin-bottom: 30px; text-align: center; }}
        .privacy-banner h3 {{ color: #92400e; margin-bottom: 10px; }}
        .privacy-banner p {{ color: #92400e; margin: 0; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 20px; border-radius: 12px; text-align: center; border: 2px solid #667eea; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 5px; }}
        .stat-label {{ color: #666; font-weight: 600; }}
        .case-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
        .case-card {{ background: white; border: 2px solid #e9ecef; border-radius: 12px; padding: 20px; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }}
        .case-card:hover {{ transform: translateY(-5px); border-color: #667eea; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2); }}
        .case-id {{ font-size: 1.3em; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
        .case-info {{ color: #666; margin-bottom: 15px; font-size: 0.95em; }}
        .case-link {{ display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; text-decoration: none; padding: 10px 20px; border-radius: 25px; font-weight: 600; transition: all 0.3s ease; }}
        .case-link:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3); }}
        .generation-info {{ background: #f0f9ff; border: 2px solid #0891b2; border-radius: 12px; padding: 20px; margin-bottom: 30px; }}
        .generation-info h3 {{ color: #0891b2; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 医学诊断打分系统</h1>
        </div>
        
        <div class="privacy-banner">
            <h3>🔒 已打分项目会自动保存，若一次填不完可放心退出。（需在浏览器中打开页面）</h3>
        </div>
                
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(generated_files)}</div>
                <div class="stat-label">病例总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(case['doctor_count'] for case in generated_files)}</div>
                <div class="stat-label">医师诊断总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">9</div>
                <div class="stat-label">评分字段数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{sum(case['doctor_count'] for case in generated_files) * 9}</div>
                <div class="stat-label">总评分项数</div>
            </div>
        </div>
        
        <h2 style="color: #333; margin-bottom: 20px;">📁 病例列表</h2>
        <div class="case-list">
"""
    
    for case in generated_files:
        summary_html += f"""
            <div class="case-card">
                <div class="case-id">病例ID: {case['case_id']}</div>
                <div class="case-info">
                    医师数量: {case['doctor_count']} 名<br>
                    评分项目: {case['doctor_count'] * 9} 个<br>
                </div>
                <a href="{case['filename']}" class="case-link" target="_blank">
                    🎯 开始评分
                </a>
            </div>
"""
    
    summary_html += """
        </div>
    </div>
</body>
</html>
"""
    
    # 保存汇总页面
    summary_path = os.path.join(output_dir, "index.html")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_html)
    
    print(f"✓ 生成汇总页面: index.html")

def main():
    """主函数"""
    print("🏥 医学诊断打分系统 - 批量网页生成器")
    print("=" * 55)
    
    # 配置文件路径
    csv_file = "data.csv"
    output_directory = "medical_scoring_pages"
    
    try:
        generated_files = process_csv_and_generate_html(csv_file, output_directory)
        
        print("\n📋 生成结果:")
        for case in generated_files:
            print(f"  • {case['case_id']}: {case['filename']} ({case['doctor_count']}名医师)")
                
    except KeyboardInterrupt:
        print(f"\n⚠️ 用户中断了程序执行")
        return 1
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())