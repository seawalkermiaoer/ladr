#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识点管理页面
提供知识点和题目知识点关联的CRUD操作界面
"""

import streamlit as st
import json
from typing import List, Dict, Any, Optional
import os
import sys

# 添加父目录到路径以导入api_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_service import api_request

def get_knowledge_points() -> List[Dict[str, Any]]:
    """获取所有知识点"""
    result = api_request("GET", "knowledge_points")
    return result if result else []

def get_questions() -> List[Dict[str, Any]]:
    """获取所有题目"""
    result = api_request("GET", "questions")
    return result if result else []

def get_question_knowledge_points() -> List[Dict[str, Any]]:
    """获取所有题目知识点关联"""
    result = api_request("GET", "question_knowledge_points")
    return result if result else []

def knowledge_point_management():
    """知识点管理界面"""
    st.header("📚 知识点管理")
    
    # 获取现有知识点
    knowledge_points = get_knowledge_points()
    
    # 显示现有知识点
    st.subheader("现有知识点")
    if knowledge_points:
        for point in knowledge_points:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{point['name']}** (ID: {point['id']})")
            with col2:
                if st.button("编辑", key=f"edit_kp_{point['id']}"):
                    st.session_state[f"edit_kp_{point['id']}"] = True
            with col3:
                if st.button("删除", key=f"delete_kp_{point['id']}"):
                    if api_request("DELETE", f"knowledge_points/{point['id']}"):
                        st.success(f"知识点 '{point['name']}' 删除成功！")
                        st.rerun()
            
            # 编辑模式
            if st.session_state.get(f"edit_kp_{point['id']}", False):
                with st.form(f"edit_form_{point['id']}"):
                    new_name = st.text_input("知识点名称", value=point['name'])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("保存"):
                            if new_name.strip():
                                update_data = {"name": new_name.strip()}
                                if api_request("PUT", f"knowledge_points/{point['id']}", update_data):
                                    st.success("知识点更新成功！")
                                    st.session_state[f"edit_kp_{point['id']}"] = False
                                    st.rerun()
                            else:
                                st.error("知识点名称不能为空")
                    with col2:
                        if st.form_submit_button("取消"):
                            st.session_state[f"edit_kp_{point['id']}"] = False
                            st.rerun()
    else:
        st.info("暂无知识点数据")
    
    # 添加新知识点
    st.subheader("添加新知识点")
    with st.form("add_knowledge_point"):
        new_point_name = st.text_input("知识点名称")
        if st.form_submit_button("添加知识点"):
            if new_point_name.strip():
                point_data = {"name": new_point_name.strip()}
                result = api_request("POST", "knowledge_points", point_data)
                if result:
                    st.success(f"知识点 '{new_point_name}' 添加成功！")
                    st.rerun()
            else:
                st.error("知识点名称不能为空")

def question_knowledge_point_management():
    """题目知识点关联管理界面"""
    st.header("🔗 题目知识点关联管理")
    
    # 获取数据
    knowledge_points = get_knowledge_points()
    questions = get_questions()
    relations = get_question_knowledge_points()
    
    # 显示现有关联
    st.subheader("现有关联")
    if relations:
        for relation in relations:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                # 查找对应的知识点名称和题目信息
                kp_name = "未知知识点"
                for kp in knowledge_points:
                    if kp['id'] == relation['knowledge_point_id']:
                        kp_name = kp['name']
                        break
                
                # 查找题目信息
                question_info = f"题目ID: {relation['question_id']}"
                for q in questions:
                    if q['id'] == relation['question_id']:
                        # 截取题目内容的前50个字符作为预览
                        content_preview = q.get('content', '')[:50] + ('...' if len(q.get('content', '')) > 50 else '')
                        question_info = f"题目: {content_preview} (ID: {relation['question_id']})"
                        break
                
                st.write(f"**{question_info}** ↔ **{kp_name}** (关联ID: {relation['id']})")
            with col2:
                if st.button("编辑", key=f"edit_rel_{relation['id']}"):
                    st.session_state[f"edit_rel_{relation['id']}"] = True
            with col3:
                if st.button("删除", key=f"delete_rel_{relation['id']}"):
                    if api_request("DELETE", f"question_knowledge_points/{relation['id']}"):
                        st.success("关联删除成功！")
                        st.rerun()
            
            # 编辑模式
            if st.session_state.get(f"edit_rel_{relation['id']}", False):
                with st.form(f"edit_rel_form_{relation['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        # 题目选择下拉框
                        if questions:
                            question_options = {}
                            current_question_index = 0
                            for i, q in enumerate(questions):
                                content_preview = q.get('content', '')[:30] + ('...' if len(q.get('content', '')) > 30 else '')
                                question_options[q['id']] = f"ID:{q['id']} - {content_preview}"
                                if q['id'] == relation['question_id']:
                                    current_question_index = i
                            
                            new_question_id = st.selectbox(
                                "选择题目",
                                options=list(question_options.keys()),
                                format_func=lambda x: question_options[x],
                                index=current_question_index,
                                key=f"edit_q_sel_{relation['id']}"
                            )
                        else:
                            st.warning("没有可用的题目")
                            new_question_id = relation['question_id']
                    with col2:
                        kp_options = {kp['id']: kp['name'] for kp in knowledge_points}
                        if kp_options:
                            current_kp_index = list(kp_options.keys()).index(relation['knowledge_point_id']) if relation['knowledge_point_id'] in kp_options else 0
                            new_kp_id = st.selectbox(
                                "知识点",
                                options=list(kp_options.keys()),
                                format_func=lambda x: kp_options[x],
                                index=current_kp_index,
                                key=f"edit_kp_sel_{relation['id']}"
                            )
                        else:
                            st.warning("没有可用的知识点")
                            new_kp_id = None
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("保存") and new_kp_id:
                            update_data = {
                                "question_id": new_question_id,
                                "knowledge_point_id": new_kp_id
                            }
                            if api_request("PUT", f"question_knowledge_points/{relation['id']}", update_data):
                                st.success("关联更新成功！")
                                st.session_state[f"edit_rel_{relation['id']}"] = False
                                st.rerun()
                    with col2:
                        if st.form_submit_button("取消"):
                            st.session_state[f"edit_rel_{relation['id']}"] = False
                            st.rerun()
    else:
        st.info("暂无题目知识点关联数据")
    
    # 添加新关联
    st.subheader("添加新关联")
    if knowledge_points and questions:
        with st.form("add_relation"):
            col1, col2 = st.columns(2)
            with col1:
                # 题目选择下拉框
                question_options = {}
                for q in questions:
                    content_preview = q.get('content', '')[:30] + ('...' if len(q.get('content', '')) > 30 else '')
                    question_options[q['id']] = f"ID:{q['id']} - {content_preview}"
                
                selected_question_id = st.selectbox(
                    "选择题目",
                    options=list(question_options.keys()),
                    format_func=lambda x: question_options[x]
                )
            with col2:
                kp_options = {kp['id']: kp['name'] for kp in knowledge_points}
                selected_kp_id = st.selectbox(
                    "选择知识点",
                    options=list(kp_options.keys()),
                    format_func=lambda x: kp_options[x]
                )
            
            if st.form_submit_button("添加关联"):
                relation_data = {
                    "question_id": selected_question_id,
                    "knowledge_point_id": selected_kp_id
                }
                result = api_request("POST", "question_knowledge_points", relation_data)
                if result:
                    st.success("题目知识点关联添加成功！")
                    st.rerun()
    elif not knowledge_points:
        st.warning("请先添加知识点，然后才能创建关联")
    elif not questions:
        st.warning("请先添加题目，然后才能创建关联")

def api_test_interface():
    """API测试界面"""
    st.header("🧪 API测试界面")
    
    # 选择API类型
    api_type = st.selectbox(
        "选择API类型",
        ["知识点API", "题目知识点关联API"]
    )
    
    if api_type == "知识点API":
        st.subheader("知识点API测试")
        
        # 选择操作类型
        operation = st.selectbox(
            "选择操作",
            ["GET - 获取所有知识点", "GET - 根据ID获取知识点", "POST - 创建知识点", "PUT - 更新知识点", "DELETE - 删除知识点"]
        )
        
        if operation == "GET - 获取所有知识点":
            if st.button("执行请求"):
                result = api_request("GET", "knowledge_points")
                if result is not None:
                    st.json(result)
        
        elif operation == "GET - 根据ID获取知识点":
            point_id = st.number_input("知识点ID", min_value=1)
            if st.button("执行请求"):
                result = api_request("GET", f"knowledge_points/{point_id}")
                if result is not None:
                    st.json(result)
        
        elif operation == "POST - 创建知识点":
            name = st.text_input("知识点名称")
            if st.button("执行请求") and name:
                data = {"name": name}
                result = api_request("POST", "knowledge_points", data)
                if result is not None:
                    st.json(result)
        
        elif operation == "PUT - 更新知识点":
            point_id = st.number_input("知识点ID", min_value=1)
            name = st.text_input("新的知识点名称")
            if st.button("执行请求") and name:
                data = {"name": name}
                result = api_request("PUT", f"knowledge_points/{point_id}", data)
                if result is not None:
                    st.json(result)
        
        elif operation == "DELETE - 删除知识点":
            point_id = st.number_input("知识点ID", min_value=1)
            if st.button("执行请求"):
                result = api_request("DELETE", f"knowledge_points/{point_id}")
                if result is not None:
                    st.json(result)
    
    else:  # 题目知识点关联API
        st.subheader("题目知识点关联API测试")
        
        operation = st.selectbox(
            "选择操作",
            ["GET - 获取所有关联", "GET - 根据ID获取关联", "POST - 创建关联", "PUT - 更新关联", "DELETE - 删除关联"]
        )
        
        if operation == "GET - 获取所有关联":
            if st.button("执行请求"):
                result = api_request("GET", "question_knowledge_points")
                if result is not None:
                    st.json(result)
        
        elif operation == "GET - 根据ID获取关联":
            relation_id = st.number_input("关联ID", min_value=1)
            if st.button("执行请求"):
                result = api_request("GET", f"question_knowledge_points/{relation_id}")
                if result is not None:
                    st.json(result)
        
        elif operation == "POST - 创建关联":
            col1, col2 = st.columns(2)
            with col1:
                question_id = st.number_input("题目ID", min_value=1)
            with col2:
                kp_id = st.number_input("知识点ID", min_value=1)
            
            if st.button("执行请求"):
                data = {"question_id": question_id, "knowledge_point_id": kp_id}
                result = api_request("POST", "question_knowledge_points", data)
                if result is not None:
                    st.json(result)
        
        elif operation == "PUT - 更新关联":
            relation_id = st.number_input("关联ID", min_value=1)
            col1, col2 = st.columns(2)
            with col1:
                question_id = st.number_input("新的题目ID", min_value=1)
            with col2:
                kp_id = st.number_input("新的知识点ID", min_value=1)
            
            if st.button("执行请求"):
                data = {"question_id": question_id, "knowledge_point_id": kp_id}
                result = api_request("PUT", f"question_knowledge_points/{relation_id}", data)
                if result is not None:
                    st.json(result)
        
        elif operation == "DELETE - 删除关联":
            relation_id = st.number_input("关联ID", min_value=1)
            if st.button("执行请求"):
                result = api_request("DELETE", f"question_knowledge_points/{relation_id}")
                if result is not None:
                    st.json(result)

def main():
    """主函数"""
    st.set_page_config(
        page_title="知识点管理",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 知识点管理系统")
    
    # 侧边栏导航
    st.sidebar.title("导航")
    page = st.sidebar.selectbox(
        "选择页面",
        ["知识点管理", "题目知识点关联管理", "API测试界面"]
    )
    
    # 显示API连接状态
    st.sidebar.markdown("---")
    st.sidebar.markdown("**API状态**")
    try:
        # 测试API连接
        test_result = api_request("GET", "knowledge_points")
        if test_result is not None:
            st.sidebar.success("✅ API连接正常")
        else:
            st.sidebar.error("❌ API响应异常")
    except:
        st.sidebar.error("❌ API连接失败")
    
    # 根据选择显示对应页面
    if page == "知识点管理":
        knowledge_point_management()
    elif page == "题目知识点关联管理":
        question_knowledge_point_management()
    elif page == "API测试界面":
        api_test_interface()

if __name__ == "__main__":
    main()
