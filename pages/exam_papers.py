import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_service import make_api_request

# 导入学生选择相关函数
try:
    from pages.student_selection import get_selected_student, is_student_selected, get_selected_student_id, get_selected_student_name
except ImportError:
    # 如果在pages目录外运行，尝试直接导入
    from student_selection import get_selected_student, is_student_selected, get_selected_student_id, get_selected_student_name

# 数据获取函数
@st.cache_data(ttl=30)
def get_students() -> List[Dict]:
    result = make_api_request("GET", "students")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_exam_papers() -> List[Dict]:
    result = make_api_request("GET", "exam_papers")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_questions() -> List[Dict]:
    result = make_api_request("GET", "questions")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_knowledge_points() -> List[Dict]:
    result = make_api_request("GET", "knowledge_points")
    return result["data"] if result["success"] else []

@st.cache_data(ttl=30)
def get_question_knowledge_points() -> List[Dict]:
    result = make_api_request("GET", "question_knowledge_points")
    return result["data"] if result["success"] else []

# 页面标题
st.title("📄 试卷管理")

# 检查登录状态
if not st.session_state.get("logged_in", False):
    st.error("❌ 请先登录才能访问试卷管理功能")
    st.info("💡 请返回首页进行登录")
    st.stop()

# 显示当前选中的学生信息
if is_student_selected():
    st.info(f"📌 当前显示学生: **{get_selected_student_name()}** 的试卷")
else:
    st.warning("⚠️ 未选择学生，显示所有试卷。建议先选择学生以获得更好的体验。")

st.markdown("---")

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
    # 获取题目数据用于统计
    all_questions = get_questions()
    
    # 为每个试卷添加学生姓名和统计信息
    papers_with_student = []
    for paper in exam_papers:
        student = next((s for s in students if s['id'] == paper['student_id']), None)
        paper_info = paper.copy()
        paper_info['student_name'] = student['name'] if student else '未知学生'
        
        # 计算错题率
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
    
    # 提示用户使用专门的详情页面
    st.info("💡 要查看试卷详情和管理题目，请使用专门的试卷详情页面")
    
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
                
                # 先删除相关的题目知识点关联
                all_questions = get_questions()
                all_question_kps = get_question_knowledge_points()
                
                # 获取该试卷的所有题目
                paper_questions = [q for q in all_questions if q['exam_paper_id'] == paper_id]
                for question in paper_questions:
                    question_kps = [qkp for qkp in all_question_kps if qkp['question_id'] == question['id']]
                    for qkp in question_kps:
                        make_api_request("DELETE", f"question_knowledge_points/{qkp['id']}")
                
                # 删除题目
                for question in paper_questions:
                    make_api_request("DELETE", f"questions/{question['id']}")
                
                # 删除试卷
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