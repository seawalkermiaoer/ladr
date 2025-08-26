import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import os
import sys
import json

# 添加父目录到路径以导入api_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_service import make_api_request

# 导入学生选择相关函数
try:
    from pages.student_selection import get_selected_student, is_student_selected, get_selected_student_id, get_selected_student_name
except ImportError:
    # 如果在pages目录内运行，直接导入
    from student_selection import get_selected_student, is_student_selected, get_selected_student_id, get_selected_student_name

# 获取数据的辅助函数
@st.cache_data(ttl=30)
def get_students() -> List[Dict]:
    """获取学生列表"""
    result = make_api_request("GET", "students")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_exam_papers() -> List[Dict]:
    """获取试卷列表"""
    result = make_api_request("GET", "exam_papers")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_exam_paper_images() -> List[Dict]:
    """获取试卷图片列表"""
    result = make_api_request("GET", "exam_paper_images")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_questions() -> List[Dict]:
    """获取题目列表"""
    result = make_api_request("GET", "questions")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_knowledge_points() -> List[Dict]:
    """获取知识点列表"""
    result = make_api_request("GET", "knowledge_points")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_question_knowledge_points() -> List[Dict]:
    """获取题目知识点关联列表"""
    result = make_api_request("GET", "question_knowledge_points")
    return result["data"] if result["success"] else []

def show_exam_paper_detail(paper_id: int):
    """显示试卷详情页面"""
    students = get_students()
    all_exam_papers = get_exam_papers()
    all_exam_paper_images = get_exam_paper_images()
    all_questions = get_questions()
    all_knowledge_points = get_knowledge_points()
    all_question_kps = get_question_knowledge_points()
    
    # 获取当前试卷信息
    current_paper = next((p for p in all_exam_papers if p['id'] == paper_id), None)
    if not current_paper:
        st.error("试卷不存在")
        return
    
    # 获取学生信息
    student = next((s for s in students if s['id'] == current_paper['student_id']), None)
    student_name = student['name'] if student else '未知学生'
    
    # 页面标题
    st.title(f"📄 {current_paper['title']}")
    st.info(f"👤 学生: {student_name} | 📅 创建时间: {current_paper.get('created_time', 'N/A')}")
    
    if current_paper.get('description'):
        st.markdown(f"**描述:** {current_paper['description']}")
    
    st.markdown("---")
    
    # 获取试卷相关的题目
    paper_questions = [q for q in all_questions if q['exam_paper_id'] == paper_id]
    
    # 计算统计信息
    total_questions = len(paper_questions)
    wrong_questions = [q for q in paper_questions if not q.get('is_correct', True)]
    wrong_count = len(wrong_questions)
    error_rate = (wrong_count / total_questions * 100) if total_questions > 0 else 0
    
    # 显示统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总题数", total_questions)
    with col2:
        st.metric("错题数", wrong_count)
    with col3:
        st.metric("正确题数", total_questions - wrong_count)
    with col4:
        st.metric("错误率", f"{error_rate:.1f}%")
    
    st.markdown("---")
    
    # 题目管理
    st.subheader("📝 题目管理")
    
    # 添加新题目
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("➕ 添加单个题目"):
            with st.form("add_question_form"):
                question_content = st.text_area("题目内容")
                is_correct = st.checkbox("答题正确", value=True)
                
                # 图片选择功能 - 从exam_paper_image表选择
                st.markdown("**选择题目相关图片（可选）:**")
                paper_images = [img for img in all_exam_paper_images if img['exam_paper_id'] == paper_id]
                
                if paper_images:
                    image_options = [f"{img['id']} - {img['image_url'].split('/')[-1]}" for img in paper_images]
                    selected_image = st.selectbox(
                        "选择图片",
                        options=["无"] + image_options,
                        key="single_question_image"
                    )
                else:
                    st.info("该试卷暂无图片，请先在试卷图片管理页面上传图片")
                    selected_image = "无"
                
                # 知识点选择
                if all_knowledge_points:
                    selected_kps = st.multiselect(
                        "选择相关知识点",
                        options=[f"{kp['id']} - {kp['name']}" for kp in all_knowledge_points],
                        key="add_question_kps"
                    )
                
                submit_question = st.form_submit_button("添加题目")
                
                if submit_question and question_content:
                    # 处理选择的图片
                    content = question_content
                    selected_image_id = None
                    
                    if selected_image and selected_image != "无":
                        # 从选择的字符串中提取图片ID
                        img_id = int(selected_image.split(' - ')[0])
                        selected_image_id = img_id
                        # 找到对应的图片记录
                        img_record = next((img for img in paper_images if img['id'] == img_id), None)
                        if img_record:
                            content += f"\n\n![题目图片]({img_record['image_url']})"
                    elif paper_images:
                        # 如果没有选择图片但试卷有图片，使用第一张图片
                        selected_image_id = paper_images[0]['id']
                        content += f"\n\n![题目图片]({paper_images[0]['image_url']})"
                    
                    # 验证必需的image_id
                    if not selected_image_id:
                        st.error("添加失败: 该试卷没有图片，无法创建题目")
                        return
                    
                    # 添加题目，包含必需的image_id和student_id字段
                    result = make_api_request("POST", "questions", {
                        "content": content,
                        "is_correct": is_correct,
                        "exam_paper_id": paper_id,
                        "image_id": selected_image_id,
                        "student_id": get_selected_student_id()
                    })
                    
                    if result["success"]:
                        question_id = result["data"]["id"]
                        
                        # 添加知识点关联
                        if all_knowledge_points and selected_kps:
                            for kp_option in selected_kps:
                                kp_id = int(kp_option.split(" - ")[0])
                                make_api_request("POST", "question_knowledge_points", {
                                    "question_id": question_id,
                                    "knowledge_point_id": kp_id
                                })
                        
                        st.success("题目添加成功！")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"添加失败: {result['error']}")
    
    with col2:
        with st.expander("📝 批量添加题目"):
            with st.form("batch_add_questions_form"):
                # 调试模式开关
                debug_mode = st.checkbox("启用调试模式（显示详细错误信息）", key="debug_mode_checkbox")
                if debug_mode:
                    st.session_state['debug_mode'] = True
                else:
                    st.session_state.pop('debug_mode', None)
                
                st.markdown("**JSON格式示例:**")
                st.code('''
[
  {"content": "题目内容1", "is_correct": true},
  {"content": "题目内容2", "is_correct": false},
  {"content": "题目内容3", "is_correct": true}
]''')
                
                batch_json = st.text_area(
                    "题目JSON数据",
                    height=200,
                    help="请输入符合格式的JSON数据，每个题目包含content和is_correct字段"
                )
                
                # 图片选择功能 - 从exam_paper_image表选择
                st.markdown("**选择题目相关图片（可选）:**")
                paper_images = [img for img in all_exam_paper_images if img['exam_paper_id'] == paper_id]
                
                if paper_images:
                    image_options = [f"{img['id']} - {img['image_url'].split('/')[-1]}" for img in paper_images]
                    selected_images = st.multiselect(
                        "选择图片",
                        options=image_options,
                        key="batch_question_images"
                    )
                else:
                    st.info("该试卷暂无图片，请先在试卷图片管理页面上传图片")
                    selected_images = []
                
                # 知识点选择
                if all_knowledge_points:
                    batch_selected_kps = st.multiselect(
                        "选择相关知识点（应用到所有题目）",
                        options=[f"{kp['id']} - {kp['name']}" for kp in all_knowledge_points],
                        key="batch_add_question_kps"
                    )
                
                submit_batch = st.form_submit_button("批量添加题目")
                
                if submit_batch and batch_json:
                    try:
                        questions_data = json.loads(batch_json)
                        
                        if not isinstance(questions_data, list):
                            st.error("JSON数据必须是数组格式")
                        else:
                            # 处理选择的图片
                            image_urls = []
                            if selected_images:
                                for selected_img in selected_images:
                                    # 从选择的字符串中提取图片ID
                                    img_id = int(selected_img.split(' - ')[0])
                                    # 找到对应的图片记录
                                    img_record = next((img for img in paper_images if img['id'] == img_id), None)
                                    if img_record:
                                        image_urls.append(img_record['image_url'])
                            
                            # 批量添加题目
                            success_count = 0
                            error_count = 0
                            
                            # 显示调试信息
                            st.info(f"准备添加 {len(questions_data)} 个题目，可用图片 {len(image_urls)} 个")
                            
                            for i, question_data in enumerate(questions_data):
                                try:
                                    if not isinstance(question_data, dict):
                                        st.error(f"第{i+1}个题目数据格式错误，必须是对象")
                                        error_count += 1
                                        continue
                                    
                                    if 'content' not in question_data:
                                        st.error(f"第{i+1}个题目缺少content字段")
                                        error_count += 1
                                        continue
                                    
                                    # 验证content不为空
                                    if not question_data['content'] or not question_data['content'].strip():
                                        st.error(f"第{i+1}个题目内容不能为空")
                                        error_count += 1
                                        continue
                                    
                                    # 添加题目内容，如果有图片URL则循环使用
                                    content = question_data['content']
                                    selected_image_id = None
                                    
                                    if image_urls and selected_images:
                                        # 使用模运算循环使用图片，避免索引越界
                                        image_index = i % len(selected_images)
                                        selected_img_option = selected_images[image_index]
                                        # 从选择的字符串中提取图片ID
                                        selected_image_id = int(selected_img_option.split(' - ')[0])
                                        # 找到对应的图片记录
                                        img_record = next((img for img in paper_images if img['id'] == selected_image_id), None)
                                        if img_record:
                                            content += f"\n\n![题目图片]({img_record['image_url']})"
                                    elif paper_images:
                                        # 如果没有选择图片但试卷有图片，使用第一张图片
                                        selected_image_id = paper_images[0]['id']
                                        content += f"\n\n![题目图片]({paper_images[0]['image_url']})"
                                    
                                    # 验证必需的image_id
                                    if not selected_image_id:
                                        st.error(f"第{i+1}个题目添加失败: 该试卷没有图片，无法创建题目")
                                        error_count += 1
                                        continue
                                    
                                    # 构建请求数据，包含必需的image_id字段
                                    request_data = {
                                        "content": content,
                                        "is_correct": question_data.get('is_correct', True),
                                        "exam_paper_id": paper_id,
                                        "image_id": selected_image_id,
                                        "student_id": get_selected_student_id()
                                    }
                                    
                                    # 显示详细的请求信息（仅在调试时）
                                    if st.session_state.get('debug_mode', False):
                                        st.write(f"第{i+1}个题目请求数据:", request_data)
                                    
                                    result = make_api_request("POST", "questions", request_data)
                                    
                                    if result["success"]:
                                        question_id = result["data"]["id"]
                                        
                                        # 添加知识点关联
                                        if all_knowledge_points and batch_selected_kps:
                                            for kp_option in batch_selected_kps:
                                                try:
                                                    kp_id = int(kp_option.split(" - ")[0])
                                                    kp_result = make_api_request("POST", "question_knowledge_points", {
                                                        "question_id": question_id,
                                                        "knowledge_point_id": kp_id
                                                    })
                                                    if not kp_result["success"]:
                                                        st.warning(f"第{i+1}个题目的知识点关联失败: {kp_result.get('error', '未知错误')}")
                                                except Exception as kp_e:
                                                    st.warning(f"第{i+1}个题目的知识点关联出现异常: {str(kp_e)}")
                                        
                                        success_count += 1
                                        st.success(f"✅ 第{i+1}个题目添加成功")
                                    else:
                                        error_msg = result.get('error', '未知错误')
                                        st.error(f"❌ 第{i+1}个题目添加失败: {error_msg}")
                                        
                                        # 显示更详细的错误信息
                                        if 'details' in result:
                                            st.error(f"详细错误信息: {result['details']}")
                                        
                                        error_count += 1
                                        
                                except Exception as e:
                                    st.error(f"❌ 第{i+1}个题目处理过程中出现异常: {str(e)}")
                                    error_count += 1
                            
                            if success_count > 0:
                                st.success(f"成功添加 {success_count} 个题目！")
                                st.cache_data.clear()
                                st.rerun()
                            
                            if error_count > 0:
                                st.warning(f"有 {error_count} 个题目添加失败")
                    
                    except json.JSONDecodeError as e:
                        st.error(f"JSON格式错误: {str(e)}")
                    except Exception as e:
                        st.error(f"批量添加过程中出现错误: {str(e)}")
    
    # 题目列表
    st.subheader("📋 题目列表")
    
    # 创建包含知识点信息的题目数据
    questions_with_kps = []
    for question in paper_questions:
        question_info = question.copy()
        
        # 获取题目相关的知识点
        question_kps = [qkp for qkp in all_question_kps if qkp['question_id'] == question['id']]
        kp_names = []
        for qkp in question_kps:
            kp = next((k for k in all_knowledge_points if k['id'] == qkp['knowledge_point_id']), None)
            if kp:
                kp_names.append(kp['name'])
        
        question_info['knowledge_points'] = ', '.join(kp_names) if kp_names else '无'
        question_info['status'] = '✅ 正确' if question.get('is_correct', True) else '❌ 错误'
        questions_with_kps.append(question_info)
    
    # 按创建时间排序
    questions_with_kps.sort(key=lambda x: x.get('created_time', ''), reverse=True)
    
    # 显示题目表格
    questions_df = pd.DataFrame(questions_with_kps)
    if not questions_df.empty:
        columns_order = ['id', 'content', 'status', 'knowledge_points', 'created_time']
        available_columns = [col for col in columns_order if col in questions_df.columns]
        questions_df = questions_df[available_columns]
    
    st.dataframe(questions_df, use_container_width=True)
    
    # 题目操作
    st.subheader("题目操作")
    col1, col2 = st.columns(2)
    
    with col1:
        # 编辑题目
        with st.expander("✏️ 编辑题目"):
            question_to_edit = st.selectbox(
                "选择要编辑的题目",
                options=[f"{q['id']} - {q['content'][:30]}..." for q in paper_questions],
                key="edit_question_select"
            )
            
            if question_to_edit:
                question_id = int(question_to_edit.split(" - ")[0])
                current_question = next((q for q in paper_questions if q['id'] == question_id), None)
                
                if current_question:
                    with st.form("edit_question_form"):
                        edit_content = st.text_area("题目内容", value=current_question['content'])
                        edit_is_correct = st.checkbox("答题正确", value=current_question.get('is_correct', True))
                        
                        # 当前知识点
                        current_question_kps = [qkp for qkp in all_question_kps if qkp['question_id'] == question_id]
                        current_kp_ids = [qkp['knowledge_point_id'] for qkp in current_question_kps]
                        current_kp_options = [f"{kp['id']} - {kp['name']}" for kp in all_knowledge_points if kp['id'] in current_kp_ids]
                        
                        if all_knowledge_points:
                            edit_selected_kps = st.multiselect(
                                "选择相关知识点",
                                options=[f"{kp['id']} - {kp['name']}" for kp in all_knowledge_points],
                                default=current_kp_options,
                                key="edit_question_kps"
                            )
                        
                        submit_edit_question = st.form_submit_button("更新题目")
                        
                        if submit_edit_question and edit_content:
                            # 更新题目
                            result = make_api_request("PUT", f"questions/{question_id}", {
                                "content": edit_content,
                                "is_correct": edit_is_correct,
                                "exam_paper_id": paper_id
                            })
                            
                            if result["success"]:
                                # 删除旧的知识点关联
                                for qkp in current_question_kps:
                                    make_api_request("DELETE", f"question_knowledge_points/{qkp['id']}")
                                
                                # 添加新的知识点关联
                                if all_knowledge_points and edit_selected_kps:
                                    for kp_option in edit_selected_kps:
                                        kp_id = int(kp_option.split(" - ")[0])
                                        make_api_request("POST", "question_knowledge_points", {
                                            "question_id": question_id,
                                            "knowledge_point_id": kp_id
                                        })
                                
                                st.success("题目更新成功！")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(f"更新失败: {result['error']}")
    
    with col2:
        # 删除题目
        with st.expander("🗑️ 删除题目"):
            question_to_delete = st.selectbox(
                "选择要删除的题目",
                options=[f"{q['id']} - {q['content'][:30]}..." for q in paper_questions],
                key="delete_question_select"
            )
            
            if st.button("删除题目", type="secondary"):
                question_id = int(question_to_delete.split(" - ")[0])
                
                # 删除题目相关的知识点关联
                question_kps = [qkp for qkp in all_question_kps if qkp['question_id'] == question_id]
                for qkp in question_kps:
                    make_api_request("DELETE", f"question_knowledge_points/{qkp['id']}")
                
                # 删除题目
                result = make_api_request("DELETE", f"questions/{question_id}")
                if result["success"]:
                    st.success("题目删除成功！")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"删除失败: {result['error']}")
    
    # 如果没有题目，显示提示信息
    if not paper_questions:
        st.info("该试卷暂无题目，可以使用上面的功能添加题目")

# 主页面
st.title("📄 试卷详情")

# 检查用户是否已登录
if not st.session_state.get("logged_in", False):
    st.error("❌ 请先登录才能访问试卷详情功能")
    st.info("💡 请返回首页进行登录")
    st.stop()

# 获取所有试卷数据
all_exam_papers = get_exam_papers()

if not all_exam_papers:
    st.warning("⚠️ 暂无试卷数据")
    st.info("💡 请先在试卷管理页面创建试卷")
    st.stop()

# 试卷筛选功能
st.subheader("🔍 选择试卷")

# 试卷名称筛选
search_term = st.text_input(
    "按试卷名称筛选",
    placeholder="输入试卷名称进行搜索...",
    key="paper_search"
)

# 根据搜索条件筛选试卷
filtered_papers = all_exam_papers
if search_term:
    filtered_papers = [
        paper for paper in all_exam_papers 
        if search_term.lower() in paper.get('title', '').lower()
    ]

if not filtered_papers:
    st.warning("⚠️ 没有找到匹配的试卷")
    st.info("💡 请尝试其他搜索关键词")
    st.stop()

# 试卷选择下拉框
paper_options = [f"{paper['id']} - {paper.get('title', '未命名试卷')}" for paper in filtered_papers]
selected_paper_option = st.selectbox(
    "选择要查看的试卷",
    options=paper_options,
    key="selected_paper"
)

if selected_paper_option:
    # 从选择的选项中提取试卷ID
    paper_id = int(selected_paper_option.split(' - ')[0])
    
    st.markdown("---")
    
    # 显示试卷详情
    show_exam_paper_detail(paper_id)
else:
    st.info("💡 请选择要查看的试卷")