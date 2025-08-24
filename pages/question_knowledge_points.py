#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目知识点关联管理页面
提供题目知识点关联的CRUD操作界面
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

def main():
    """主函数"""
    st.set_page_config(
        page_title="题目知识点关联管理",
        page_icon="🔗",
        layout="wide"
    )
    
    st.title("🔗 题目知识点关联管理")
    
    # 获取数据
    knowledge_points = get_knowledge_points()
    questions = get_questions()
    relations = get_question_knowledge_points()
    
    # 显示API连接状态
    with st.sidebar:
        st.markdown("**API状态**")
        try:
            # 测试API连接
            test_result = api_request("GET", "question_knowledge_points")
            if test_result is not None:
                st.success("✅ API连接正常")
            else:
                st.error("❌ API响应异常")
        except:
            st.error("❌ API连接失败")
    
    # 显示现有关联
    st.header("现有关联")
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
                                content_preview = q.get('content', '')[:50] + ('...' if len(q.get('content', '')) > 50 else '')
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
    st.header("添加新关联")
    if knowledge_points and questions:
        with st.form("add_relation"):
            col1, col2 = st.columns(2)
            with col1:
                # 题目选择下拉框
                question_options = {}
                for q in questions:
                    content_preview = q.get('content', '')[:50] + ('...' if len(q.get('content', '')) > 50 else '')
                    question_options[q['id']] = f"ID:{q['id']} - {content_preview}"
                
                question_id = st.selectbox(
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
                    "question_id": question_id,
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
    
    # 统计信息
    st.header("统计信息")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("知识点总数", len(knowledge_points))
    with col2:
        st.metric("题目总数", len(questions))
    with col3:
        st.metric("关联总数", len(relations))

if __name__ == "__main__":
    main()