#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识点管理页面
提供知识点的增删改查功能
"""

import streamlit as st
import sys
import os
from typing import List, Dict, Any, Optional

# 添加父目录到路径以导入api_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_service import api_request

def get_knowledge_points() -> List[Dict[str, Any]]:
    """获取所有知识点"""
    return api_request("GET", "knowledge_points") or []

def knowledge_point_management():
    """知识点管理主界面"""
    st.title("知识点管理")
    
    # 添加新知识点
    st.subheader("添加新知识点")
    with st.form("add_knowledge_point_form"):
        new_name = st.text_input("知识点名称", placeholder="请输入知识点名称")
        if st.form_submit_button("添加知识点"):
            if new_name.strip():
                create_data = {"name": new_name.strip()}
                result = api_request("POST", "knowledge_points", create_data)
                if result:
                    st.success(f"知识点 '{result.get('name', new_name.strip())}' 添加成功！")
                    st.rerun()
                else:
                    st.error("添加失败，请检查网络连接或数据库配置")
            else:
                st.error("知识点名称不能为空")
    
    st.divider()
    
    # 显示现有知识点
    st.subheader("现有知识点")
    knowledge_points = get_knowledge_points()
    
    if knowledge_points:
        # 搜索功能
        search_term = st.text_input("搜索知识点", placeholder="输入关键词搜索...")
        
        # 过滤知识点
        if search_term:
            filtered_points = [
                point for point in knowledge_points 
                if search_term.lower() in point['name'].lower()
            ]
        else:
            filtered_points = knowledge_points
        
        if filtered_points:
            st.write(f"共找到 {len(filtered_points)} 个知识点")
            
            for point in filtered_points:
                # 检查是否有更新成功的标记
                if st.session_state.get(f"updated_kp_{point['id']}", False):
                    st.success(f"知识点 '{point['name']}' 更新成功！")
                    # 清除标记
                    del st.session_state[f"updated_kp_{point['id']}"]
                
                # 检查是否处于编辑模式
                edit_mode = st.session_state.get(f"edit_kp_{point['id']}", False)
                
                if not edit_mode:
                    # 显示模式
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{point['name']}** (ID: {point['id']})")
                    with col2:
                        if st.button("编辑", key=f"edit_btn_{point['id']}"):
                            st.session_state[f"edit_kp_{point['id']}"] = True
                            st.rerun()
                    with col3:
                        if st.button("删除", key=f"delete_btn_{point['id']}", type="secondary"):
                            # 确认删除
                            st.session_state[f"confirm_delete_{point['id']}"] = True
                            st.rerun()
                else:
                    # 编辑模式
                    with st.form(f"edit_form_{point['id']}"):
                        new_name = st.text_input("知识点名称", value=point['name'])
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("保存"):
                                if new_name.strip():
                                    update_data = {"name": new_name.strip()}
                                    result = api_request("PUT", f"knowledge_points/{point['id']}", update_data)
                                    if result:
                                        st.success(f"知识点更新成功！新名称: {result.get('name', new_name.strip())}")
                                        # 先设置状态再重新运行
                                        st.session_state[f"edit_kp_{point['id']}"] = False
                                        # 添加一个标记表示更新成功
                                        st.session_state[f"updated_kp_{point['id']}"] = True
                                        st.rerun()
                                    else:
                                        st.error("更新失败，请检查网络连接或数据库配置")
                                else:
                                    st.error("知识点名称不能为空")
                        with col2:
                            if st.form_submit_button("取消"):
                                st.session_state[f"edit_kp_{point['id']}"] = False
                                st.rerun()
                
                # 处理删除确认
                if st.session_state.get(f"confirm_delete_{point['id']}", False):
                    st.warning(f"确定要删除知识点 '{point['name']}' 吗？此操作不可撤销！")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("确认删除", key=f"confirm_del_{point['id']}", type="primary"):
                            result = api_request("DELETE", f"knowledge_points/{point['id']}")
                            if result:
                                st.success(f"知识点 '{point['name']}' 删除成功！")
                                # 清除相关状态
                                if f"confirm_delete_{point['id']}" in st.session_state:
                                    del st.session_state[f"confirm_delete_{point['id']}"]
                                st.rerun()
                            else:
                                st.error("删除失败，请检查网络连接或数据库配置")
                    with col2:
                        if st.button("取消删除", key=f"cancel_del_{point['id']}"):
                            del st.session_state[f"confirm_delete_{point['id']}"]
                            st.rerun()
                
                st.divider()
        else:
            st.info(f"没有找到包含 '{search_term}' 的知识点")
    else:
        st.info("暂无知识点数据，请先添加一些知识点")

def main():
    """主函数"""
    # 检查用户是否已登录
    if 'user_id' not in st.session_state:
        st.error("请先登录")
        st.stop()
    
    knowledge_point_management()

if __name__ == "__main__":
    main()