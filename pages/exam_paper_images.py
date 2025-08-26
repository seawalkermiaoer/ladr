import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import os
import sys
from PIL import Image

# 添加父目录到路径以导入api_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_service import make_api_request
from cos_uploader import ExamPaperCOSManager

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

# 主页面
st.title("🖼️ 试卷图片管理")

# 检查用户是否已登录
if not st.session_state.get("logged_in", False):
    st.error("❌ 请先登录才能访问试卷图片管理功能")
    st.info("💡 请返回首页进行登录")
    st.stop()

# 显示当前选中的学生信息（仅在登录后）
if is_student_selected():
    st.info(f"📌 当前显示学生: **{get_selected_student_name()}** 的试卷图片")
else:
    st.warning("⚠️ 未选择学生，显示所有试卷图片。建议先选择学生以获得更好的体验。")

st.markdown("---")

# 获取相关数据
students = get_students()
all_exam_papers = get_exam_papers()
all_exam_paper_images = get_exam_paper_images()

# 根据选中的学生筛选试卷
if is_student_selected():
    selected_student_id = get_selected_student_id()
    exam_papers = [paper for paper in all_exam_papers if paper['student_id'] == selected_student_id]
else:
    exam_papers = all_exam_papers

# 试卷选择器
if exam_papers:
    st.subheader("📋 选择试卷")
    paper_options = [f"{paper['id']} - {paper['title']}" for paper in exam_papers]
    selected_paper_option = st.selectbox(
        "选择要查看图片的试卷",
        options=paper_options,
        key="image_view_paper_select"
    )
    
    if selected_paper_option:
        selected_paper_id = int(selected_paper_option.split(" - ")[0])
        selected_paper = next((p for p in exam_papers if p['id'] == selected_paper_id), None)
        
        # 筛选选中试卷的图片
        exam_paper_images = [img for img in all_exam_paper_images if img['exam_paper_id'] == selected_paper_id]
        
        st.info(f"📌 当前查看试卷: **{selected_paper['title']}** 的图片")
        
        # 图片列表
        if exam_paper_images:
            # 创建包含试卷标题的图片数据
            images_with_paper = []
            for image in exam_paper_images:
                paper = next((p for p in exam_papers if p['id'] == image['exam_paper_id']), None)
                image_info = image.copy()
                image_info['paper_title'] = paper['title'] if paper else '未知试卷'
                images_with_paper.append(image_info)
            
            # 按上传顺序排序
            images_with_paper.sort(key=lambda x: x.get('upload_order', 0))
            
            st.subheader(f"📸 试卷图片列表 (共 {len(images_with_paper)} 张)")
            
            # 图片列表显示（默认不加载图片）
            cols_per_row = 2
            for i in range(0, len(images_with_paper), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(images_with_paper):
                        image_info = images_with_paper[i + j]
                        with cols[j]:
                            # 创建图片信息卡片
                            with st.container():
                                st.markdown(f"### 📷 图片 #{image_info.get('upload_order', 'N/A')}")
                                st.caption(f"**ID:** {image_info['id']} | **试卷:** {image_info['paper_title']}")
                                
                                # 图片预览按钮
                                if st.button(f"👁️ 查看图片详情", key=f"view_image_{image_info['id']}", type="primary"):
                                    # 在session_state中存储要显示的图片ID
                                    if 'viewing_image_id' not in st.session_state:
                                        st.session_state.viewing_image_id = set()
                                    
                                    if image_info['id'] in st.session_state.viewing_image_id:
                                        st.session_state.viewing_image_id.remove(image_info['id'])
                                    else:
                                        st.session_state.viewing_image_id.add(image_info['id'])
                                    st.rerun()
                                
                                # 如果图片被选中显示，则加载图片
                                if ('viewing_image_id' in st.session_state and 
                                    image_info['id'] in st.session_state.viewing_image_id):
                                    
                                    try:
                                        # 使用COS管理器生成安全的预签名URL
                                        cos_manager = ExamPaperCOSManager()
                                        
                                        # 从完整URL中提取文件名
                                        if 'cos.ap-guangzhou.myqcloud.com' in image_info['image_url']:
                                            # 提取COS文件路径
                                            filename = image_info['image_url'].split('.myqcloud.com/')[-1]
                                            # 生成预签名URL
                                            safe_url = cos_manager.get_safe_image_url(filename, use_presigned=True, expires_in=7200)
                                            st.image(safe_url, use_container_width=True)
                                        else:
                                            # 如果不是COS URL，直接使用原URL
                                            st.image(image_info['image_url'], use_container_width=True)
                                        
                                        # 隐藏图片按钮
                                        if st.button(f"🙈 隐藏图片", key=f"hide_image_{image_info['id']}", type="secondary"):
                                            st.session_state.viewing_image_id.remove(image_info['id'])
                                            st.rerun()
                                    
                                    except Exception as e:
                                        # 显示错误信息
                                        st.error(f"❌ 图片加载失败: {str(e)}")
                                        st.info("🔗 图片链接可能已失效或无法访问")
                                        
                                        # 显示完整URL以便调试
                                        with st.expander("🔍 查看详细信息"):
                                            st.text("完整URL:")
                                            st.code(image_info['image_url'], language=None)
                                            st.text("错误详情:")
                                            st.code(str(e), language=None)
                                            
                                            # 提供删除选项
                                            if st.button(f"🗑️ 删除此图片记录", key=f"delete_{image_info['id']}", type="secondary"):
                                                try:
                                                    delete_result = make_api_request("DELETE", f"exam_paper_images/{image_info['id']}")
                                                    if delete_result["success"]:
                                                        st.success("✅ 图片记录已删除")
                                                        # 从viewing_image_id中移除
                                                        if image_info['id'] in st.session_state.viewing_image_id:
                                                            st.session_state.viewing_image_id.remove(image_info['id'])
                                                        st.cache_data.clear()
                                                        st.rerun()
                                                    else:
                                                        st.error(f"删除失败: {delete_result['error']}")
                                                except Exception as del_e:
                                                    st.error(f"删除操作失败: {str(del_e)}")
                                
                                # 访问链接（始终显示）
                                with st.expander("🔗 访问链接"):
                                    st.code(image_info['image_url'], language=None)
                                    if st.button(f"📋 复制链接", key=f"copy_{image_info['id']}"):
                                        st.success("链接已复制到剪贴板！")
                                        st.code(f"navigator.clipboard.writeText('{image_info['image_url']}')", language="javascript")
                                
                                st.markdown("---")
            
            # 数据表格（可选显示）
            with st.expander("📊 详细数据表格"):
                images_df = pd.DataFrame(images_with_paper)
                if not images_df.empty:
                    columns_order = ['id', 'paper_title', 'image_url', 'upload_order', 'exam_paper_id']
                    available_columns = [col for col in columns_order if col in images_df.columns]
                    images_df = images_df[available_columns]
                
                st.dataframe(images_df, use_container_width=True)
        
        # 图片上传功能
        st.subheader("📤 上传更多图片")
        
        # 文件上传组件
        uploaded_files = st.file_uploader(
            "选择图片文件",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            accept_multiple_files=True,
            key="exam_paper_images_uploader"
        )
        
        if uploaded_files:
            # 显示预览
            st.subheader("📷 图片预览")
            cols = st.columns(min(len(uploaded_files), 3))
            for i, uploaded_file in enumerate(uploaded_files):
                with cols[i % 3]:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name, use_container_width=True)
            
            # 上传按钮
            if st.button("🚀 上传所有图片", type="primary", key="upload_images_btn"):
                try:
                    cos_manager = ExamPaperCOSManager()
                    success_count = 0
                    error_messages = []
                    
                    # 获取当前试卷的最大上传顺序
                    current_images = [img for img in exam_paper_images if img['exam_paper_id'] == selected_paper_id]
                    max_order = max([img.get('upload_order', 0) for img in current_images], default=0)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(uploaded_files):
                        try:
                            status_text.text(f"正在上传: {uploaded_file.name}")
                            
                            # 重置文件指针
                            uploaded_file.seek(0)
                            
                            # 上传到COS
                            upload_result = cos_manager.upload_image(
                                uploaded_file,
                                filename=None  # 使用自动生成的文件名
                            )
                            
                            if upload_result['success']:
                                # 保存到数据库
                                db_result = make_api_request("POST", "exam_paper_images", {
                                    "image_url": upload_result['url'],
                                    "upload_order": max_order + i + 1,
                                    "exam_paper_id": selected_paper_id
                                })
                                
                                if db_result["success"]:
                                    success_count += 1
                                else:
                                    error_messages.append(f"{uploaded_file.name}: 数据库保存失败 - {db_result['error']}")
                            else:
                                error_messages.append(f"{uploaded_file.name}: 上传失败 - {upload_result.get('error', '未知错误')}")
                        
                        except Exception as e:
                            error_messages.append(f"{uploaded_file.name}: {str(e)}")
                        
                        # 更新进度
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    # 显示结果
                    status_text.empty()
                    progress_bar.empty()
                    
                    if success_count > 0:
                        st.success(f"✅ 成功上传 {success_count} 张图片！")
                        st.cache_data.clear()
                        st.rerun()
                    
                    if error_messages:
                        st.error("❌ 部分图片上传失败：")
                        for error in error_messages:
                            st.error(f"• {error}")
                
                except Exception as e:
                    st.error(f"❌ 上传过程中发生错误: {str(e)}")
else:
    # 如果没有试卷，显示上传第一张图片的功能
    st.info("暂无试卷数据")
    
    if exam_papers:
        st.subheader("📤 上传第一张试卷图片")
        paper_options = [f"{paper['id']} - {paper['title']}" for paper in exam_papers]
        first_selected_paper = st.selectbox("选择试卷", options=paper_options, key="first_upload_paper_select")
        
        # 文件上传组件
        first_uploaded_files = st.file_uploader(
            "选择图片文件",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            accept_multiple_files=True,
            key="first_exam_paper_images_uploader"
        )
        
        if first_uploaded_files and first_selected_paper:
            paper_id = int(first_selected_paper.split(" - ")[0])
            
            # 显示预览
            st.subheader("📷 图片预览")
            cols = st.columns(min(len(first_uploaded_files), 3))
            for i, uploaded_file in enumerate(first_uploaded_files):
                with cols[i % 3]:
                    image = Image.open(uploaded_file)
                    st.image(image, caption=uploaded_file.name, use_container_width=True)
            
            # 上传按钮
            if st.button("🚀 上传所有图片", type="primary", key="first_upload_images_btn"):
                try:
                    cos_manager = ExamPaperCOSManager()
                    success_count = 0
                    error_messages = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, uploaded_file in enumerate(first_uploaded_files):
                        try:
                            status_text.text(f"正在上传: {uploaded_file.name}")
                            
                            # 重置文件指针
                            uploaded_file.seek(0)
                            
                            # 上传到COS
                            upload_result = cos_manager.upload_image(
                                uploaded_file,
                                filename=None  # 使用自动生成的文件名
                            )
                            
                            if upload_result['success']:
                                # 保存到数据库
                                db_result = make_api_request("POST", "exam_paper_images", {
                                    "image_url": upload_result['url'],
                                    "upload_order": i + 1,
                                    "exam_paper_id": paper_id
                                })
                                
                                if db_result["success"]:
                                    success_count += 1
                                else:
                                    error_messages.append(f"{uploaded_file.name}: 数据库保存失败 - {db_result['error']}")
                            else:
                                error_messages.append(f"{uploaded_file.name}: 上传失败 - {upload_result.get('error', '未知错误')}")
                        
                        except Exception as e:
                            error_messages.append(f"{uploaded_file.name}: {str(e)}")
                        
                        # 更新进度
                        progress_bar.progress((i + 1) / len(first_uploaded_files))
                    
                    # 显示结果
                    status_text.empty()
                    progress_bar.empty()
                    
                    if success_count > 0:
                        st.success(f"✅ 成功上传 {success_count} 张图片！")
                        st.cache_data.clear()
                        st.rerun()
                    
                    if error_messages:
                        st.error("❌ 部分图片上传失败：")
                        for error in error_messages:
                            st.error(f"• {error}")
                
                except Exception as e:
                    st.error(f"❌ 上传过程中发生错误: {str(e)}")
    else:
        st.warning("请先添加试卷才能上传图片")

st.markdown("---")
if st.button("🔄 刷新数据", type="primary", key="refresh_images"):
    st.cache_data.clear()
    st.rerun()