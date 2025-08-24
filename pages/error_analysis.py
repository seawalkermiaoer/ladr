import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
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

# 加载环境变量
load_dotenv()

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
def get_exam_paper_images() -> List[Dict]:
    """获取试卷图片列表"""
    result = make_api_request("GET", "exam_paper_images")
    return result["data"] if result["success"] else []

def calculate_error_rate(student_id: int, exam_paper_id: int, questions: List[Dict]) -> Dict:
    """计算错题比例"""
    # 过滤出该学生在该试卷上的题目
    exam_questions = [q for q in questions 
                     if q.get('exam_paper_id') == exam_paper_id 
                     and q.get('student_id') == student_id]
    
    if not exam_questions:
        return {"total_questions": 0, "error_questions": 0, "error_rate": 0, "error_list": []}
    
    # 根据数据库中的is_correct字段判断错题
    error_questions = []
    for question in exam_questions:
        # 如果is_correct为False或None，则认为是错题
        if not question.get('is_correct', False):
            error_questions.append(question)
    
    total_questions = len(exam_questions)
    error_count = len(error_questions)
    error_rate = (error_count / total_questions * 100) if total_questions > 0 else 0
    
    return {
        "total_questions": total_questions,
        "error_questions": error_count,
        "error_rate": error_rate,
        "error_list": error_questions
    }

def calculate_trend_analysis(student_id: int, start_date: str, end_date: str, 
                           exam_papers: List[Dict], questions: List[Dict]) -> Dict:
    """计算指定时间范围内的错题趋势分析"""
    # 过滤时间范围内的试卷
    filtered_papers = []
    for paper in exam_papers:
        if paper.get('student_id') == student_id and paper.get('created_time'):
            try:
                # 解析试卷创建时间
                paper_date = datetime.fromisoformat(paper['created_time'].replace('Z', '+00:00'))
                start_dt = datetime.fromisoformat(start_date + 'T00:00:00+00:00')
                end_dt = datetime.fromisoformat(end_date + 'T23:59:59+00:00')
                
                if start_dt <= paper_date <= end_dt:
                    filtered_papers.append(paper)
            except (ValueError, TypeError):
                continue
    
    # 计算每张试卷的错题率
    trend_data = []
    for paper in filtered_papers:
        paper_questions = [q for q in questions if q.get('exam_paper_id') == paper['id']]
        
        if paper_questions:
            total_count = len(paper_questions)
            error_count = sum(1 for q in paper_questions if not q.get('is_correct', False))
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            
            trend_data.append({
                'paper_id': paper['id'],
                'paper_title': paper.get('title', f'试卷{paper["id"]}'),
                'created_time': paper['created_time'],
                'total_questions': total_count,
                'error_questions': error_count,
                'error_rate': error_rate,
                'correct_rate': 100 - error_rate
            })
    
    # 按时间排序
    trend_data.sort(key=lambda x: x['created_time'])
    
    return {
        'papers_in_range': len(filtered_papers),
        'trend_data': trend_data,
        'total_questions_all': sum(item['total_questions'] for item in trend_data),
        'total_errors_all': sum(item['error_questions'] for item in trend_data),
        'average_error_rate': sum(item['error_rate'] for item in trend_data) / len(trend_data) if trend_data else 0
    }

def main():
    st.title("📊 错题分析")
    
    # 显示当前筛选的学生信息
    if is_student_selected():
        selected_student = get_selected_student()
        st.info(f"🎯 当前筛选学生: **{selected_student['name']}** (ID: {selected_student['id']})")
    else:
        st.warning("⚠️ 未选择学生，将显示所有学生的数据。请先在学生选择页面选择一个学生。")
    
    st.markdown("---")
    
    # 获取数据
    students = get_students()
    exam_papers = get_exam_papers()
    questions = get_questions()
    exam_paper_images = get_exam_paper_images()
    
    if not students:
        st.error("无法获取学生数据")
        return
    
    if not exam_papers:
        st.error("无法获取试卷数据")
        return
    
    # 根据选中的学生筛选数据
    if is_student_selected():
        selected_student_id = get_selected_student_id()
        # 筛选该学生的试卷
        filtered_exam_papers = [ep for ep in exam_papers if ep.get('student_id') == selected_student_id]
        # 筛选该学生的题目
        filtered_questions = [q for q in questions if q.get('student_id') == selected_student_id]
    else:
        filtered_exam_papers = exam_papers
        filtered_questions = questions
    
    # 创建选项卡
    tab1, tab2 = st.tabs(["📋 单卷错题分析", "📈 错题趋势分析"])
    
    with tab1:
        # 创建两列布局
        col1, col2 = st.columns(2)
    
        with col1:
            # 学生选择
            if is_student_selected():
                selected_student = get_selected_student()
                st.info(f"已选择学生: **{selected_student['name']}**")
                selected_student_id = selected_student['id']
            else:
                student_options = {f"{s['name']} (ID: {s['id']})": s['id'] for s in students}
                selected_student_display = st.selectbox(
                    "选择学生",
                    options=list(student_options.keys()),
                    key="error_analysis_student_select"
                )
                selected_student_id = student_options[selected_student_display] if selected_student_display else None
        
        with col2:
            # 试卷选择 - 根据选中的学生筛选试卷
            if selected_student_id:
                student_exam_papers = [ep for ep in filtered_exam_papers if ep.get('student_id') == selected_student_id]
                if student_exam_papers:
                    exam_paper_options = {f"{ep['title']} (ID: {ep['id']})": ep['id'] for ep in student_exam_papers}
                    selected_exam_paper_display = st.selectbox(
                        "选择试卷",
                        options=list(exam_paper_options.keys()),
                        key="error_analysis_exam_paper_select"
                    )
                    selected_exam_paper_id = exam_paper_options[selected_exam_paper_display] if selected_exam_paper_display else None
                else:
                    st.warning("该学生暂无试卷数据")
                    selected_exam_paper_id = None
            else:
                st.info("请先选择学生")
                selected_exam_paper_id = None
    
        if selected_student_id and selected_exam_paper_id:
            st.markdown("---")
            
            # 计算错题分析
            error_analysis = calculate_error_rate(selected_student_id, selected_exam_paper_id, filtered_questions)
            
            # 显示错题比例
            st.subheader("📈 错题统计")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总题数", error_analysis["total_questions"])
            with col2:
                st.metric("错题数", error_analysis["error_questions"])
            with col3:
                st.metric("错题率", f"{error_analysis['error_rate']:.1f}%")
            with col4:
                correct_rate = 100 - error_analysis['error_rate']
                st.metric("正确率", f"{correct_rate:.1f}%")
            
            # 错题率进度条
            st.progress(error_analysis['error_rate'] / 100)
            
            st.markdown("---")
            
            # 显示错题列表
            if error_analysis["error_list"]:
                st.subheader("❌ 错题列表")
                
                for i, question in enumerate(error_analysis["error_list"], 1):
                    with st.expander(f"错题 {i}: {question.get('content', '无题目内容')[:50]}..."):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**题目ID:** {question['id']}")
                            st.write(f"**题目内容:** {question.get('content', '无内容')}")
                            st.write(f"**答题状态:** {'❌ 错误' if not question.get('is_correct', False) else '✅ 正确'}")
                            if question.get('remark'):
                                st.write(f"**错题备注:** {question['remark']}")
                            
                            # 显示时间信息
                            if question.get('created_time'):
                                st.write(f"**创建时间:** {question['created_time']}")
                            if question.get('updated_time'):
                                st.write(f"**更新时间:** {question['updated_time']}")
                        
                        with col2:
                            # 查找该题目对应的图片
                            question_image_id = question.get('image_id')
                            if question_image_id:
                                # 根据image_id查找对应的图片
                                question_image = next(
                                    (img for img in exam_paper_images if img.get('id') == question_image_id), 
                                    None
                                )
                                
                                if question_image and question_image.get('image_url'):
                                    st.write("**题目图片:**")
                                    st.markdown(f"[查看原图]({question_image['image_url']})")
                                    # 显示缩略图
                                    try:
                                        st.image(question_image['image_url'], width=200, caption="题目原图")
                                    except:
                                        st.write(f"图片链接: {question_image['image_url']}")
                                else:
                                    st.write("暂无题目图片")
                            else:
                                st.write("暂无关联图片ID")
            else:
                st.success("🎉 恭喜！该学生在此试卷上没有错题！")
        
        else:
            st.info("请选择学生和试卷以查看错题分析")
    
    with tab2:
        st.header("📈 错题趋势分析")
        
        # 学生选择
        if is_student_selected():
            selected_student = get_selected_student()
            st.info(f"已选择学生: **{selected_student['name']}**")
            selected_student_trend_id = selected_student['id']
        else:
            student_options_trend = {f"{s['name']} (ID: {s['id']})": s['id'] for s in students}
            selected_student_trend = st.selectbox(
                "选择学生",
                options=list(student_options_trend.keys()),
                key="trend_analysis_student_select"
            )
            selected_student_trend_id = student_options_trend[selected_student_trend] if selected_student_trend else None
        
        # 时间范围选择
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "开始日期",
                value=datetime.now() - timedelta(days=30),
                key="trend_start_date"
            )
        with col2:
            end_date = st.date_input(
                "结束日期",
                value=datetime.now(),
                key="trend_end_date"
            )
        
        if selected_student_trend_id and start_date and end_date:
            if start_date <= end_date:
                # 计算趋势分析
                trend_analysis = calculate_trend_analysis(
                    selected_student_trend_id, 
                    start_date.isoformat(), 
                    end_date.isoformat(),
                    filtered_exam_papers, 
                    filtered_questions
                )
                
                if trend_analysis['trend_data']:
                    st.markdown("---")
                    
                    # 显示总体统计
                    st.subheader("📊 总体统计")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("时间范围内试卷数", trend_analysis['papers_in_range'])
                    with col2:
                        st.metric("总题目数", trend_analysis['total_questions_all'])
                    with col3:
                        st.metric("总错题数", trend_analysis['total_errors_all'])
                    with col4:
                        st.metric("平均错题率", f"{trend_analysis['average_error_rate']:.1f}%")
                    
                    st.markdown("---")
                    
                    # 创建趋势图表
                    st.subheader("📈 错题率趋势图（按周分组）")
                    
                    # 准备图表数据
                    trend_df = pd.DataFrame(trend_analysis['trend_data'])
                    trend_df['date'] = pd.to_datetime(trend_df['created_time'])
                    
                    # 按周分组聚合数据
                    trend_df['week'] = trend_df['date'].dt.to_period('W').dt.start_time
                    weekly_data = trend_df.groupby('week').agg({
                        'total_questions': 'sum',
                        'error_questions': 'sum',
                        'paper_title': 'count'  # 统计该周的试卷数量
                    }).reset_index()
                    
                    # 计算每周的错题率
                    weekly_data['error_rate'] = (weekly_data['error_questions'] / weekly_data['total_questions'] * 100).fillna(0)
                    weekly_data['correct_rate'] = 100 - weekly_data['error_rate']
                    weekly_data['week_str'] = weekly_data['week'].dt.strftime('%Y年第%U周')
                    
                    # 错题率趋势线图
                    fig_line = px.line(
                        weekly_data, 
                        x='week_str', 
                        y='error_rate',
                        title='错题率变化趋势（按周统计）',
                        labels={'week_str': '周次', 'error_rate': '错题率 (%)'},
                        markers=True
                    )
                    fig_line.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_line, use_container_width=True)
                    
                    # 错题数与总题数对比柱状图（按周）
                    st.subheader("📊 每周错题数与总题数对比")
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        name='总题数',
                        x=weekly_data['week_str'],
                        y=weekly_data['total_questions'],
                        marker_color='lightblue'
                    ))
                    fig_bar.add_trace(go.Bar(
                        name='错题数',
                        x=weekly_data['week_str'],
                        y=weekly_data['error_questions'],
                        marker_color='salmon'
                    ))
                    fig_bar.update_layout(
                        title='各周错题数与总题数对比',
                        xaxis_title='周次',
                        yaxis_title='题目数量',
                        barmode='group',
                        height=400,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                    
                    # 详细数据表格（按周）
                    st.subheader("📋 每周统计数据")
                    display_weekly_df = weekly_data[['week_str', 'paper_title', 'total_questions', 'error_questions', 'error_rate', 'correct_rate']].copy()
                    display_weekly_df.columns = ['周次', '试卷数量', '总题数', '错题数', '错题率(%)', '正确率(%)']
                    display_weekly_df['错题率(%)'] = display_weekly_df['错题率(%)'].round(1)
                    display_weekly_df['正确率(%)'] = display_weekly_df['正确率(%)'].round(1)
                    st.dataframe(display_weekly_df, use_container_width=True)
                    
                    # 原始数据表格（按试卷）
                    with st.expander("📋 查看原始试卷数据"):
                        original_display_df = trend_df[['paper_title', 'date', 'total_questions', 'error_questions', 'error_rate', 'correct_rate']].copy()
                        original_display_df['date'] = original_display_df['date'].dt.date
                        original_display_df.columns = ['试卷标题', '日期', '总题数', '错题数', '错题率(%)', '正确率(%)']
                        original_display_df['错题率(%)'] = original_display_df['错题率(%)'].round(1)
                        original_display_df['正确率(%)'] = original_display_df['正确率(%)'].round(1)
                        st.dataframe(original_display_df, use_container_width=True)
                    
                else:
                    st.info("在选定的时间范围内没有找到该学生的试卷数据")
            else:
                st.error("开始日期不能晚于结束日期")
        else:
            st.info("请选择学生和时间范围以查看趋势分析")

if __name__ == "__main__":
    main()
else:
    # 当作为页面模块导入时调用
    main()