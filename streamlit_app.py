import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import sys

# 添加当前目录到路径以导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api_service import make_api_request
from pages.login import show_login_page, check_login, show_logout_button

# 加载环境变量
load_dotenv()



# 获取环境变量
ENV = os.getenv("ENV", "local")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
OBSIDIAN_KEY = os.getenv("obsidian_key", "")
OBSIDIAN_HOST = os.getenv("obsidian_host", "http://localhost:27123")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")



# 页面配置
st.set_page_config(
    page_title="ladr",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 获取数据的辅助函数

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



def show_env_info():
    """显示环境变量信息"""
    with st.sidebar:
        with st.expander("🔧 环境配置信息"):
            st.write(f"**环境**: {ENV}")
            st.write(f"**API地址**: {API_BASE_URL}")
            st.write(f"**Streamlit端口**: {STREAMLIT_SERVER_PORT}")
            st.write(f"**Streamlit地址**: {STREAMLIT_SERVER_ADDRESS}")
            st.write(f"**Obsidian主机**: {OBSIDIAN_HOST}")
            st.write(f"**Obsidian密钥**: {'已配置' if OBSIDIAN_KEY else '未配置'}")
            st.write(f"**Supabase URL**: {'已配置' if SUPABASE_URL else '未配置'}")
            st.write(f"**Supabase Key**: {'已配置' if SUPABASE_KEY else '未配置'}")

# 主应用逻辑
if not check_login():
    show_login_page()
else:
    # 显示登出按钮
    show_logout_button()
    
    # 显示环境配置信息（所有环境下都显示）
    show_env_info()
    
    # 显示当前选中的学生信息
    if 'selected_student' in st.session_state:
        with st.sidebar:
            st.markdown("### 👤 当前学生")
            selected = st.session_state.selected_student
            st.info(f"**{selected['name']}** (ID: {selected['id']})")
            if st.button("重新选择学生", key="reselect_student"):
                # 清除选择并跳转到学生选择页面
                del st.session_state.selected_student
                st.rerun()
    
    # 定义页面
    student_selection_page = st.Page(
        "pages/student_selection.py", 
        title="选择学生", 
        icon="🎓"
    )
    exam_papers_page = st.Page(
        "pages/exam_papers.py", 
        title="试卷管理", 
        icon="📄"
    )

    error_analysis_page = st.Page(
        "pages/error_analysis.py", 
        title="错题分析", 
        icon="📊"
    )
    knowledge_points_page = st.Page(
        "pages/knowledge_points.py", 
        title="知识点管理", 
        icon="📚"
    )
    question_knowledge_points_page = st.Page(
        "pages/question_knowledge_points.py", 
        title="题目知识点关联", 
        icon="🔗"
    )
    
    # 创建导航
    pg = st.navigation([
        student_selection_page,
        exam_papers_page,
        error_analysis_page,
        knowledge_points_page,
        question_knowledge_points_page
    ])
    
    # 运行页面
    pg.run()