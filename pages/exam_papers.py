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
    # 获取数据
    all_exam_papers = get_exam_papers()
    all_questions = get_questions()
    all_knowledge_points = get_knowledge_points()
    all_question_kps = get_question_knowledge_points()
    
    # 找到当前试卷
    current_paper = next((p for p in all_exam_papers if p['id'] == paper_id), None)
    if not current_paper:
        st.error("试卷不存在")
        return
    
    # 返回按钮
    if st.button("← 返回试卷列表", type="secondary"):
        st.session_state.exam_paper_view_mode = 'list'
        st.session_state.selected_exam_paper_id = None
        st.rerun()
    
    st.header(f"📄 试卷详情: {current_paper['title']}")
    
    # 试卷基本信息
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**试卷ID:** {current_paper['id']}")
        st.info(f"**创建时间:** {current_paper.get('created_time', 'N/A')}")
    with col2:
        st.info(f"**描述:** {current_paper.get('description', '无描述')}")
    
    st.markdown("---")
    
    # 获取该试卷的所有题目
    paper_questions = [q for q in all_questions if q['exam_paper_id'] == paper_id]
    
    if paper_questions:
        # 添加题目过滤选项
        st.subheader("🔍 题目筛选")
        filter_option = st.selectbox(
            "按正确性筛选题目",
            options=["全部题目", "正确题目", "错误题目"],
            index=2,  # 默认选择"错误题目"
            key="question_filter"
        )
        
        # 根据筛选条件过滤题目
        if filter_option == "正确题目":
            filtered_questions = [q for q in paper_questions if q.get('is_correct', True)]
        elif filter_option == "错误题目":
            filtered_questions = [q for q in paper_questions if not q.get('is_correct', True)]
        else:
            filtered_questions = paper_questions
        
        st.subheader(f"📝 题目列表 (共 {len(filtered_questions)} 道题 / 总计 {len(paper_questions)} 道题)")
        
        # 为每道题目创建编辑界面
        for i, question in enumerate(filtered_questions, 1):
            with st.expander(f"题目 {i} (ID: {question['id']})", expanded=False):
                # 获取该题目的知识点
                question_kp_ids = [qkp['knowledge_point_id'] for qkp in all_question_kps if qkp['question_id'] == question['id']]
                question_kps = [kp for kp in all_knowledge_points if kp['id'] in question_kp_ids]
                
                # 编辑题目表单
                with st.form(f"edit_question_{question['id']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_content = st.text_area("题目内容", value=question.get('content', ''), key=f"content_{question['id']}")
                        edit_is_correct = st.selectbox(
                            "是否正确", 
                            options=[True, False], 
                            index=0 if question.get('is_correct', True) else 1,
                            key=f"correct_{question['id']}"
                        )
                    
                    with col2:
                        edit_note = st.text_area("备注", value=question.get('note', ''), key=f"note_{question['id']}")
                        
                        # 知识点选择
                        if all_knowledge_points:
                            kp_options = [f"{kp['id']} - {kp['name']}" for kp in all_knowledge_points]
                            current_kp_options = [f"{kp['id']} - {kp['name']}" for kp in question_kps]
                            selected_kps = st.multiselect(
                                "关联知识点",
                                options=kp_options,
                                default=current_kp_options,
                                key=f"kps_{question['id']}"
                            )
                    
                    col_update, col_delete = st.columns(2)
                    with col_update:
                        if st.form_submit_button("更新题目", type="primary"):
                            # 更新题目
                            result = make_api_request("PUT", f"questions/{question['id']}", {
                                "content": edit_content,
                                "is_correct": edit_is_correct,
                                "note": edit_note,
                                "exam_paper_id": paper_id
                            })
                            
                            if result["success"]:
                                # 更新知识点关联
                                if all_knowledge_points and 'selected_kps' in locals():
                                    # 删除旧的关联
                                    for qkp in all_question_kps:
                                        if qkp['question_id'] == question['id']:
                                            make_api_request("DELETE", f"question_knowledge_points/{qkp['id']}")
                                    
                                    # 添加新的关联
                                    for kp_option in selected_kps:
                                        kp_id = int(kp_option.split(" - ")[0])
                                        make_api_request("POST", "question_knowledge_points", {
                                            "question_id": question['id'],
                                            "knowledge_point_id": kp_id
                                        })
                                
                                st.success("题目更新成功！")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(f"更新失败: {result['error']}")
                    
                    with col_delete:
                        if st.form_submit_button("删除题目", type="secondary"):
                            # 删除题目知识点关联
                            for qkp in all_question_kps:
                                if qkp['question_id'] == question['id']:
                                    make_api_request("DELETE", f"question_knowledge_points/{qkp['id']}")
                            
                            # 删除题目
                            result = make_api_request("DELETE", f"questions/{question['id']}")
                            if result["success"]:
                                st.success("题目删除成功！")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(f"删除失败: {result['error']}")
        

    else:
        st.info("该试卷暂无题目")

# 主页面
st.title("📄 试卷管理")

# 初始化会话状态
if 'exam_paper_view_mode' not in st.session_state:
    st.session_state.exam_paper_view_mode = 'list'  # 'list' 或 'detail'
if 'selected_exam_paper_id' not in st.session_state:
    st.session_state.selected_exam_paper_id = None

# 显示当前选中的学生信息
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
    # 创建标签页
    tab1, tab2 = st.tabs(["📋 试卷管理", "🖼️ 试卷图片管理"])

    with tab1:
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
            # 创建包含学生姓名的试卷数据
            papers_with_student = []
            for paper in exam_papers:
                student = next((s for s in students if s['id'] == paper['student_id']), None)
                paper_info = paper.copy()
                paper_info['student_name'] = student['name'] if student else '未知学生'
                papers_with_student.append(paper_info)
            
            papers_df = pd.DataFrame(papers_with_student)
            # 重新排列列的顺序
            if not papers_df.empty:
                columns_order = ['id', 'title', 'description', 'student_name', 'student_id', 'created_time']
                available_columns = [col for col in columns_order if col in papers_df.columns]
                papers_df = papers_df[available_columns]
            
            st.dataframe(papers_df, use_container_width=True)
            
            # 试卷详情查看
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
                # 添加试卷
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
                        result = make_api_request("DELETE", f"exam_papers/{paper_id}")
                        if result["success"]:
                            st.success("试卷删除成功！")
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

    with tab2:
        st.header("🖼️ 试卷图片管理")
        
        # 获取相关数据
        students = get_students()
        all_exam_papers = get_exam_papers()
        all_exam_paper_images = get_exam_paper_images()
        
        # 根据选中的学生筛选试卷和图片
        if is_student_selected():
            selected_student_id = get_selected_student_id()
            exam_papers = [paper for paper in all_exam_papers if paper['student_id'] == selected_student_id]
            # 筛选属于这些试卷的图片
            filtered_paper_ids = [paper['id'] for paper in exam_papers]
            exam_paper_images = [img for img in all_exam_paper_images if img['exam_paper_id'] in filtered_paper_ids]
        else:
            exam_papers = all_exam_papers
            exam_paper_images = all_exam_paper_images
        
        # 图片列表
        if exam_paper_images:
            # 创建包含试卷标题的图片数据
            images_with_paper = []
            for image in exam_paper_images:
                paper = next((p for p in exam_papers if p['id'] == image['exam_paper_id']), None)
                image_info = image.copy()
                image_info['paper_title'] = paper['title'] if paper else '未知试卷'
                images_with_paper.append(image_info)
            
            images_df = pd.DataFrame(images_with_paper)
            # 重新排列列的顺序
            if not images_df.empty:
                columns_order = ['id', 'paper_title', 'image_url', 'upload_order', 'exam_paper_id']
                available_columns = [col for col in columns_order if col in images_df.columns]
                images_df = images_df[available_columns]
            
            st.dataframe(images_df, use_container_width=True)
            
            # 图片操作
            st.subheader("图片操作")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # 添加图片
                with st.expander("➕ 添加新图片"):
                    if exam_papers:
                        with st.form("add_image_form"):
                            image_url = st.text_input("图片URL")
                            upload_order = st.number_input("上传顺序", min_value=1, value=1)
                            paper_options = [f"{paper['id']} - {paper['title']}" for paper in exam_papers]
                            selected_paper = st.selectbox("选择试卷", options=paper_options)
                            submit_image = st.form_submit_button("添加图片")
                            
                            if submit_image and image_url and selected_paper:
                                paper_id = int(selected_paper.split(" - ")[0])
                                result = make_api_request("POST", "exam_paper_images", {
                                    "image_url": image_url,
                                    "upload_order": upload_order,
                                    "exam_paper_id": paper_id
                                })
                                if result["success"]:
                                    st.success("图片添加成功！")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"添加失败: {result['error']}")
                    else:
                        st.warning("请先添加试卷才能上传图片")
            
            with col2:
                # 编辑图片
                with st.expander("✏️ 编辑图片"):
                    image_to_edit = st.selectbox(
                        "选择要编辑的图片",
                        options=[f"{img['id']} - {img['image_url'][:50]}..." for img in exam_paper_images],
                        key="edit_image_select"
                    )
                    
                    if image_to_edit:
                        image_id = int(image_to_edit.split(" - ")[0])
                        current_image = next((img for img in exam_paper_images if img['id'] == image_id), None)
                        
                        if current_image:
                            with st.form("edit_image_form"):
                                edit_image_url = st.text_input("图片URL", value=current_image['image_url'])
                                edit_upload_order = st.number_input("上传顺序", min_value=1, value=current_image.get('upload_order', 1))
                                
                                if exam_papers:
                                    current_paper_option = f"{current_image['exam_paper_id']} - {next((p['title'] for p in exam_papers if p['id'] == current_image['exam_paper_id']), '未知试卷')}"
                                    paper_options = [f"{paper['id']} - {paper['title']}" for paper in exam_papers]
                                    current_index = paper_options.index(current_paper_option) if current_paper_option in paper_options else 0
                                    edit_selected_paper = st.selectbox("选择试卷", options=paper_options, index=current_index)
                                
                                submit_edit_image = st.form_submit_button("更新图片")
                                
                                if submit_edit_image and edit_image_url:
                                    paper_id = int(edit_selected_paper.split(" - ")[0]) if exam_papers else current_image['exam_paper_id']
                                    result = make_api_request("PUT", f"exam_paper_images/{image_id}", {
                                        "image_url": edit_image_url,
                                        "upload_order": edit_upload_order,
                                        "exam_paper_id": paper_id
                                    })
                                    if result["success"]:
                                        st.success("图片更新成功！")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error(f"更新失败: {result['error']}")
            
            with col3:
                # 删除图片
                with st.expander("🗑️ 删除图片"):
                    image_to_delete = st.selectbox(
                        "选择要删除的图片",
                        options=[f"{img['id']} - {img['image_url'][:50]}..." for img in exam_paper_images],
                        key="delete_image_select"
                    )
                    
                    if st.button("删除图片", type="secondary"):
                        image_id = int(image_to_delete.split(" - ")[0])
                        result = make_api_request("DELETE", f"exam_paper_images/{image_id}")
                        if result["success"]:
                            st.success("图片删除成功！")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"删除失败: {result['error']}")
        else:
            st.info("暂无试卷图片数据")
            
            # 添加第一个图片
            if exam_papers:
                st.subheader("添加第一个图片")
                with st.form("first_image_form"):
                    first_image_url = st.text_input("图片URL")
                    first_upload_order = st.number_input("上传顺序", min_value=1, value=1)
                    paper_options = [f"{paper['id']} - {paper['title']}" for paper in exam_papers]
                    first_selected_paper = st.selectbox("选择试卷", options=paper_options)
                    submit_first_image = st.form_submit_button("添加图片")
                    
                    if submit_first_image and first_image_url and first_selected_paper:
                        paper_id = int(first_selected_paper.split(" - ")[0])
                        result = make_api_request("POST", "exam_paper_images", {
                            "image_url": first_image_url,
                            "upload_order": first_upload_order,
                            "exam_paper_id": paper_id
                        })
                        if result["success"]:
                            st.success("图片添加成功！")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"添加失败: {result['error']}")
            else:
                st.warning("请先添加试卷才能上传图片")

# 刷新按钮
st.markdown("---")
if st.button("🔄 刷新数据", type="primary", key="refresh_papers"):
    st.cache_data.clear()
    st.rerun()