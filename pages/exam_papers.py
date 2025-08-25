import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import os
import sys

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
    all_questions = get_questions()
    all_knowledge_points = get_knowledge_points()
    all_question_kps = get_question_knowledge_points()
    
    # 获取当前试卷信息
    current_paper = next((p for p in all_exam_papers if p['id'] == paper_id), None)
    if not current_paper:
        st.error("试卷不存在")
        if st.button("返回试卷列表"):
            st.session_state.exam_paper_view_mode = 'list'
            st.rerun()
        return
    
    # 获取学生信息
    student = next((s for s in students if s['id'] == current_paper['student_id']), None)
    student_name = student['name'] if student else '未知学生'
    
    # 页面标题和返回按钮
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"📄 {current_paper['title']}")
        st.info(f"👤 学生: {student_name} | 📅 创建时间: {current_paper.get('created_time', 'N/A')}")
    with col2:
        if st.button("← 返回列表", type="secondary"):
            st.session_state.exam_paper_view_mode = 'list'
            st.rerun()
    
    if current_paper.get('description'):
        st.markdown(f"**描述:** {current_paper['description']}")
    
    st.markdown("---")
    
    # 获取试卷相关的题目
    paper_questions = [q for q in all_questions if q['exam_paper_id'] == paper_id]
    
    if paper_questions:
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
        with st.expander("➕ 添加新题目"):
            with st.form("add_question_form"):
                question_content = st.text_area("题目内容")
                is_correct = st.checkbox("答题正确", value=True)
                
                # 知识点选择
                if all_knowledge_points:
                    selected_kps = st.multiselect(
                        "选择相关知识点",
                        options=[f"{kp['id']} - {kp['name']}" for kp in all_knowledge_points],
                        key="add_question_kps"
                    )
                
                submit_question = st.form_submit_button("添加题目")
                
                if submit_question and question_content:
                    # 添加题目
                    result = make_api_request("POST", "questions", {
                        "content": question_content,
                        "is_correct": is_correct,
                        "exam_paper_id": paper_id
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
    
    else:
        st.info("该试卷暂无题目")
        
        # 添加第一个题目
        st.subheader("➕ 添加第一个题目")
        with st.form("first_question_form"):
            first_question_content = st.text_area("题目内容")
            first_is_correct = st.checkbox("答题正确", value=True)
            
            # 知识点选择
            if all_knowledge_points:
                first_selected_kps = st.multiselect(
                    "选择相关知识点",
                    options=[f"{kp['id']} - {kp['name']}" for kp in all_knowledge_points],
                    key="first_question_kps"
                )
            
            submit_first_question = st.form_submit_button("添加题目")
            
            if submit_first_question and first_question_content:
                # 添加题目
                result = make_api_request("POST", "questions", {
                    "content": first_question_content,
                    "is_correct": first_is_correct,
                    "exam_paper_id": paper_id
                })
                
                if result["success"]:
                    question_id = result["data"]["id"]
                    
                    # 添加知识点关联
                    if all_knowledge_points and first_selected_kps:
                        for kp_option in first_selected_kps:
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

# 主页面
st.title("📄 试卷管理")

# 检查用户是否已登录
if not st.session_state.get("logged_in", False):
    st.error("❌ 请先登录才能访问试卷管理功能")
    st.info("💡 请返回首页进行登录")
    st.stop()

# 初始化会话状态
if 'exam_paper_view_mode' not in st.session_state:
    st.session_state.exam_paper_view_mode = 'list'  # 'list' 或 'detail'
if 'selected_exam_paper_id' not in st.session_state:
    st.session_state.selected_exam_paper_id = None

# 显示当前选中的学生信息（仅在登录后）
if is_student_selected():
    st.info(f"📌 当前显示学生: **{get_selected_student_name()}** 的试卷")
else:
    st.warning("⚠️ 未选择学生，显示所有试卷。建议先选择学生以获得更好的体验。")

st.markdown("---")

# 根据视图模式显示不同内容
if st.session_state.exam_paper_view_mode == 'detail' and st.session_state.selected_exam_paper_id:
    # 显示试卷详情页面
    show_exam_paper_detail(st.session_state.selected_exam_paper_id)
else:
    # 显示试卷列表页面
    st.header("📋 试卷管理")
    
    # 获取相关数据
    students = get_students()
    all_exam_papers = get_exam_papers()
    
    # 根据选中的学生筛选试卷
    if is_student_selected():
        selected_student_id = get_selected_student_id()
        exam_papers = [paper for paper in all_exam_papers if paper['student_id'] == selected_student_id]
    else:
        exam_papers = all_exam_papers
    
    # 试卷列表
    if exam_papers:
        # 获取所有题目数据用于计算错误率
        all_questions = get_questions()
        
        # 创建包含学生姓名和错误率的试卷数据
        papers_with_student = []
        for paper in exam_papers:
            student = next((s for s in students if s['id'] == paper['student_id']), None)
            paper_info = paper.copy()
            paper_info['student_name'] = student['name'] if student else '未知学生'
            
            # 计算错误率
            paper_questions = [q for q in all_questions if q['exam_paper_id'] == paper['id']]
            if paper_questions:
                wrong_questions = [q for q in paper_questions if not q.get('is_correct', True)]
                error_rate = len(wrong_questions) / len(paper_questions) * 100
                paper_info['error_rate'] = f"{error_rate:.1f}%"
                paper_info['total_questions'] = len(paper_questions)
                paper_info['wrong_questions'] = len(wrong_questions)
            else:
                paper_info['error_rate'] = "0.0%"
                paper_info['total_questions'] = 0
                paper_info['wrong_questions'] = 0
            
            papers_with_student.append(paper_info)
        
        # 按创建时间排序
        papers_with_student.sort(key=lambda x: x.get('created_time', ''), reverse=True)
        
        papers_df = pd.DataFrame(papers_with_student)
        # 重新排列列的顺序
        if not papers_df.empty:
            columns_order = ['id', 'title', 'error_rate', 'total_questions', 'wrong_questions', 'student_name', 'created_time', 'description', 'student_id']
            available_columns = [col for col in columns_order if col in papers_df.columns]
            papers_df = papers_df[available_columns]
        
        st.dataframe(papers_df, use_container_width=True)
        
        # 查看试卷详情
        st.subheader("📖 查看试卷详情")
        col1, col2 = st.columns([3, 1])
        with col1:
            paper_to_view = st.selectbox(
                "选择要查看详情的试卷",
                options=[f"{paper['id']} - {paper['title']}" for paper in exam_papers],
                key="view_paper_select"
            )
        with col2:
            if st.button("📖 查看详情", type="primary", key="view_detail_btn"):
                if paper_to_view:
                    paper_id = int(paper_to_view.split(" - ")[0])
                    st.session_state.exam_paper_view_mode = 'detail'
                    st.session_state.selected_exam_paper_id = paper_id
                    st.rerun()
        
        # 试卷操作
        st.subheader("试卷操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 添加新试卷
            with st.expander("➕ 添加新试卷"):
                if students:
                    with st.form("add_paper_form"):
                        paper_title = st.text_input("试卷标题")
                        paper_description = st.text_area("试卷描述")
                        
                        # 学生选择
                        if is_student_selected():
                            selected_student_info = get_selected_student()
                            st.info(f"将为学生 **{selected_student_info['name']}** 添加试卷")
                            selected_student = f"{selected_student_info['id']} - {selected_student_info['name']}"
                        else:
                            student_options = [f"{student['id']} - {student['name']}" for student in students]
                            selected_student = st.selectbox("选择学生", options=student_options)
                        
                        submit_paper = st.form_submit_button("添加试卷")
                        
                        if submit_paper and paper_title and selected_student:
                            student_id = int(selected_student.split(" - ")[0])
                            result = make_api_request("POST", "exam_papers", {
                                "title": paper_title,
                                "description": paper_description,
                                "student_id": student_id
                            })
                            if result["success"]:
                                st.success("试卷添加成功！")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(f"添加失败: {result['error']}")
                else:
                    st.warning("请先添加学生才能创建试卷")
        
        with col2:
            # 编辑试卷
            with st.expander("✏️ 编辑试卷"):
                paper_to_edit = st.selectbox(
                    "选择要编辑的试卷",
                    options=[f"{paper['id']} - {paper['title']}" for paper in exam_papers],
                    key="edit_paper_select"
                )
                
                if paper_to_edit:
                    paper_id = int(paper_to_edit.split(" - ")[0])
                    current_paper = next((p for p in exam_papers if p['id'] == paper_id), None)
                    
                    if current_paper:
                        with st.form("edit_paper_form"):
                            edit_title = st.text_input("试卷标题", value=current_paper['title'])
                            edit_description = st.text_area("试卷描述", value=current_paper.get('description', ''))
                            
                            if students:
                                current_student_option = f"{current_paper['student_id']} - {next((s['name'] for s in students if s['id'] == current_paper['student_id']), '未知学生')}"
                                student_options = [f"{student['id']} - {student['name']}" for student in students]
                                current_index = student_options.index(current_student_option) if current_student_option in student_options else 0
                                edit_selected_student = st.selectbox("选择学生", options=student_options, index=current_index)
                            
                            submit_edit = st.form_submit_button("更新试卷")
                            
                            if submit_edit and edit_title:
                                student_id = int(edit_selected_student.split(" - ")[0]) if students else current_paper['student_id']
                                result = make_api_request("PUT", f"exam_papers/{paper_id}", {
                                    "title": edit_title,
                                    "description": edit_description,
                                    "student_id": student_id
                                })
                                if result["success"]:
                                    st.success("试卷更新成功！")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"更新失败: {result['error']}")
        
        with col3:
            # 删除试卷
            with st.expander("🗑️ 删除试卷"):
                paper_to_delete = st.selectbox(
                    "选择要删除的试卷",
                    options=[f"{paper['id']} - {paper['title']}" for paper in exam_papers],
                    key="delete_paper_select"
                )
                
                if st.button("删除试卷", type="secondary"):
                    paper_id = int(paper_to_delete.split(" - ")[0])
                    
                    # 删除试卷相关的题目和知识点关联
                    all_questions = get_questions()
                    all_question_kps = get_question_knowledge_points()
                    
                    # 删除题目相关的知识点关联
                    paper_questions = [q for q in all_questions if q['exam_paper_id'] == paper_id]
                    for question in paper_questions:
                        question_kps = [qkp for qkp in all_question_kps if qkp['question_id'] == question['id']]
                        for qkp in question_kps:
                            make_api_request("DELETE", f"question_knowledge_points/{qkp['id']}")
                    
                    # 删除题目
                    for question in paper_questions:
                        make_api_request("DELETE", f"questions/{question['id']}")
                    
                    # 最后删除试卷
                    result = make_api_request("DELETE", f"exam_papers/{paper_id}")
                    if result["success"]:
                        st.success("试卷及相关数据删除成功！")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"删除失败: {result['error']}")
    else:
        st.info("暂无试卷数据")
        
        # 添加第一个试卷
        if students:
            st.subheader("添加第一个试卷")
            with st.form("first_paper_form"):
                first_paper_title = st.text_input("试卷标题")
                first_paper_description = st.text_area("试卷描述")
                
                # 学生选择
                if is_student_selected():
                    selected_student_info = get_selected_student()
                    st.info(f"将为学生 **{selected_student_info['name']}** 添加试卷")
                    first_selected_student = f"{selected_student_info['id']} - {selected_student_info['name']}"
                else:
                    student_options = [f"{student['id']} - {student['name']}" for student in students]
                    first_selected_student = st.selectbox("选择学生", options=student_options)
                
                submit_first_paper = st.form_submit_button("添加试卷")
                
                if submit_first_paper and first_paper_title and first_selected_student:
                    student_id = int(first_selected_student.split(" - ")[0])
                    result = make_api_request("POST", "exam_papers", {
                        "title": first_paper_title,
                        "description": first_paper_description,
                        "student_id": student_id
                    })
                    if result["success"]:
                        st.success("试卷添加成功！")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"添加失败: {result['error']}")
        else:
            st.warning("请先添加学生才能创建试卷")

st.markdown("---")
if st.button("🔄 刷新数据", type="primary", key="refresh_papers"):
    st.cache_data.clear()
    st.rerun()