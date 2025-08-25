#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生选择页面
用于登录后选择目标学生
"""

import streamlit as st
from typing import List, Dict, Any
import sys
import os

# 添加当前目录到路径以导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_service import make_api_request

@st.cache_data(ttl=30)
def get_students() -> List[Dict]:
    """获取学生列表"""
    result = make_api_request("GET", "students")
    return result["data"] if result["success"] else []

def show_student_selection():
    """显示学生选择页面"""
    st.title("🎓 选择学生")
    
    # 检查用户是否已登录
    if not st.session_state.get("logged_in", False):
        st.error("❌ 请先登录才能访问学生选择功能")
        st.info("💡 请返回首页进行登录")
        st.stop()
    
    st.markdown("请选择要管理的学生，选择后其他页面将默认筛选该学生的相关内容。")
    
    # 获取学生列表
    students = get_students()
    
    if not students:
        st.warning("暂无学生数据，请先添加学生信息。")
        return
    
    # 如果没有选中学生且有学生数据，自动选择第一个学生
    if not is_student_selected() and students:
        first_student = students[0]
        st.session_state.selected_student = {
            'id': first_student.get('id'),
            'name': first_student.get('name', '未知学生'),
            'user_id': first_student.get('user_id')
        }
        st.success(f"已自动选择学生: {first_student.get('name', '未知学生')}")
        st.rerun()
    
    # 创建学生选择界面
    st.markdown("### 学生列表")
    
    # 使用列布局显示学生卡片
    cols = st.columns(3)
    
    for idx, student in enumerate(students):
        col = cols[idx % 3]
        
        with col:
            with st.container():
                st.markdown(f"**{student.get('name', '未知学生')}**")
                st.markdown(f"ID: {student.get('id')}")
                
                # 选择按钮
                if st.button(
                    f"选择 {student.get('name', '未知学生')}", 
                    key=f"select_student_{student.get('id')}",
                    use_container_width=True
                ):
                    # 将选中的学生信息存储到session state
                    st.session_state.selected_student = {
                        'id': student.get('id'),
                        'name': student.get('name', '未知学生'),
                        'user_id': student.get('user_id')
                    }
                    st.success(f"已选择学生: {student.get('name', '未知学生')}")
                    st.rerun()
    
    # 显示当前选中的学生
    if 'selected_student' in st.session_state:
        st.markdown("---")
        st.markdown("### 当前选中的学生")
        selected = st.session_state.selected_student
        st.info(f"**{selected['name']}** (ID: {selected['id']})")
        
        # 提供清除选择的选项
        if st.button("清除选择", type="secondary"):
            del st.session_state.selected_student
            st.rerun()
    
    # 添加说明
    st.markdown("---")
    st.markdown("""
    ### 📝 说明
    - 选择学生后，试卷管理、题目管理、错题分析等页面将默认显示该学生的相关内容
    - 您可以随时回到此页面重新选择学生
    - 如需查看所有学生的数据，请先清除当前选择
    """)

def get_selected_student() -> Dict[str, Any]:
    """获取当前选中的学生信息"""
    return st.session_state.get('selected_student', {})

def is_student_selected() -> bool:
    """检查是否已选择学生"""
    return 'selected_student' in st.session_state and st.session_state.selected_student

def get_selected_student_id() -> int:
    """获取选中学生的ID"""
    selected = get_selected_student()
    return selected.get('id', 0) if selected else 0

def get_selected_student_name() -> str:
    """获取选中学生的姓名"""
    selected = get_selected_student()
    return selected.get('name', '') if selected else ''

# 主页面逻辑
if __name__ == "__main__":
    show_student_selection()
else:
    # 当作为模块导入时，也需要在页面运行时进行登录检查
    show_student_selection()