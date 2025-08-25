import streamlit as st
import sys
import os

# 添加父目录到路径以导入api_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_service import api_service

def show_login_page():
    """显示登录页面"""
    st.title("🔐 错误和重复的密度才是阶梯")
    st.markdown("---")
    
    # 创建居中的登录表单
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("登录")
        
        # 创建登录表单
        with st.form("login_form"):
            username = st.text_input(
                "用户名", 
                placeholder="请输入用户名",
                help="默认用户名: admin"
            )
            password = st.text_input(
                "密码", 
                type="password", 
                placeholder="请输入密码",
                help="请输入您的密码"
            )
            
            # 登录按钮
            submit_button = st.form_submit_button(
                "登录", 
                use_container_width=True,
                type="primary"
            )
            
            if submit_button:
                if username and password:
                    # 使用数据库验证用户
                    user = api_service.authenticate_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user.get('id')
                        st.success("登录成功！正在跳转...")
                        st.rerun()
                    else:
                        st.error("❌ 用户名或密码错误，请重试。")
                else:
                    st.error("❌ 请输入用户名和密码。")
        
        # 添加一些说明信息
        st.markdown("---")
        st.info("💡 错误是触发神经可塑性的唯一钥匙；没有错误，大脑就默认“一切正常”，不会升级回路。")
        st.info("🔑 10 分钟高能错误练习 > 2 小时无脑重复")

def check_login():
    """检查登录状态"""
    return st.session_state.get("logged_in", False)

def logout():
    """登出功能"""
    st.session_state.logged_in = False
    if "username" in st.session_state:
        del st.session_state.username
    st.rerun()

def show_logout_button():
    """显示登出按钮"""
    with st.sidebar:
        st.markdown("---")
        username = st.session_state.get("username", "用户")
        st.write(f"👤 欢迎, {username}")
        
        if st.button("🚪 登出", use_container_width=True):
            logout()