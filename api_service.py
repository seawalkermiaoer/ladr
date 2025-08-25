#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API服务模块
提供统一的API接口，直接调用本地的API路由函数
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# 导入本地模块
from models import (
    UserCreate, UserUpdate, UserResponse,
    StudentCreate, StudentUpdate, StudentResponse,
    ExamPaperCreate, ExamPaperUpdate, ExamPaperResponse,
    ExamPaperImageCreate, ExamPaperImageUpdate, ExamPaperImageResponse,
    KnowledgePointCreate, KnowledgePointUpdate, KnowledgePointResponse,
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionKnowledgePointCreate, QuestionKnowledgePointUpdate, QuestionKnowledgePointResponse,
    BatchQuestionCreate
)
from supabase_handler import SupabaseHandler

# 初始化数据库处理器
db_handler = SupabaseHandler()

class APIService:
    """API服务类，提供所有数据操作接口"""
    
    def __init__(self):
        self.db = db_handler
    
    # Users API
    def get_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        try:
            result = self.db.select_data("user")
            return result if result is not None else []
        except Exception as e:
            return []
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        try:
            result = self.db.select_data("user", filters={"id": user_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建用户"""
        try:
            user = UserCreate(**user_data)
            result = self.db.insert_data("user", user.model_dump())
            return result[0] if result else None
        except Exception as e:
            return None
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新用户"""
        try:
            user = UserUpdate(**user_data)
            result = self.db.update_data("user", user.model_dump(exclude_unset=True), {"id": user_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            result = self.db.delete_data("user", {"id": user_id})
            return result is not None
        except Exception as e:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """验证用户登录凭据"""
        try:
            print(f"[DEBUG] 尝试验证用户: {username}")
            # 根据用户名查询用户
            result = self.db.select_data("user", filters={"username": username})
            print(f"[DEBUG] 数据库查询结果: {result}")
            
            if not result:
                print(f"[DEBUG] 未找到用户: {username}")
                return None
            
            user = result[0]
            print(f"[DEBUG] 找到用户: {user.get('username')}, ID: {user.get('id')}")
            print(f"[DEBUG] 数据库密码哈希: {user.get('password_hash')}")
            print(f"[DEBUG] 输入密码: {password}")
            
            # 这里应该使用密码哈希验证，但为了简化，先直接比较
            # 在生产环境中应该使用bcrypt等库进行密码哈希验证
            if user.get("password_hash") == password:
                print(f"[DEBUG] 密码验证成功")
                return user
            else:
                print(f"[DEBUG] 密码验证失败")
            return None
        except Exception as e:
            print(f"[ERROR] 验证用户时发生异常: {e}")
            return None
    
    # Students API
    def get_students(self) -> List[Dict[str, Any]]:
        """获取所有学生"""
        try:
            result = self.db.select_data("student")
            return result if result is not None else []
        except Exception as e:
            return []
    
    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取学生"""
        try:
            result = self.db.select_data("student", filters={"id": student_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def create_student(self, student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建学生"""
        try:
            student = StudentCreate(**student_data)
            result = self.db.insert_data("student", student.model_dump())
            return result[0] if result else None
        except Exception as e:
            return None
    
    def update_student(self, student_id: int, student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新学生"""
        try:
            student = StudentUpdate(**student_data)
            result = self.db.update_data("student", student.model_dump(exclude_unset=True), {"id": student_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def delete_student(self, student_id: int) -> bool:
        """删除学生"""
        try:
            result = self.db.delete_data("student", {"id": student_id})
            return result is not None
        except Exception as e:
            return False
    
    # Exam Papers API
    def get_exam_papers(self) -> List[Dict[str, Any]]:
        """获取所有试卷"""
        try:
            result = self.db.select_data("exam_paper")
            return result if result is not None else []
        except Exception as e:
            return []
    
    def get_exam_paper(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取试卷"""
        try:
            result = self.db.select_data("exam_paper", filters={"id": paper_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def create_exam_paper(self, paper_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建试卷"""
        try:
            paper = ExamPaperCreate(**paper_data)
            result = self.db.insert_data("exam_paper", paper.model_dump())
            return result[0] if result else None
        except Exception as e:
            return None
    
    def update_exam_paper(self, paper_id: int, paper_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新试卷"""
        try:
            paper = ExamPaperUpdate(**paper_data)
            result = self.db.update_data("exam_paper", paper.model_dump(exclude_unset=True), {"id": paper_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def delete_exam_paper(self, paper_id: int) -> bool:
        """删除试卷"""
        try:
            result = self.db.delete_data("exam_paper", {"id": paper_id})
            return result is not None
        except Exception as e:
            return False
    
    # Exam Paper Images API
    def get_exam_paper_images(self) -> List[Dict[str, Any]]:
        """获取所有试卷图片"""
        try:
            result = self.db.select_data("exam_paper_image")
            return result if result is not None else []
        except Exception as e:
            return []
    
    def get_exam_paper_image(self, image_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取试卷图片"""
        try:
            result = self.db.select_data("exam_paper_image", filters={"id": image_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def create_exam_paper_image(self, image_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建试卷图片"""
        try:
            image = ExamPaperImageCreate(**image_data)
            result = self.db.insert_data("exam_paper_image", image.model_dump())
            return result[0] if result else None
        except Exception as e:
            return None
    
    def update_exam_paper_image(self, image_id: int, image_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新试卷图片"""
        try:
            image = ExamPaperImageUpdate(**image_data)
            result = self.db.update_data("exam_paper_image", image.model_dump(exclude_unset=True), {"id": image_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def delete_exam_paper_image(self, image_id: int) -> bool:
        """删除试卷图片"""
        try:
            result = self.db.delete_data("exam_paper_image", {"id": image_id})
            return result is not None
        except Exception as e:
            return False
    
    # Knowledge Points API
    def get_knowledge_points(self) -> List[Dict[str, Any]]:
        """获取所有知识点"""
        try:
            result = self.db.select_data("knowledge_point")
            return result if result is not None else []
        except Exception as e:
            return []
    
    def get_knowledge_point(self, point_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取知识点"""
        try:
            result = self.db.select_data("knowledge_point", filters={"id": point_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def create_knowledge_point(self, point_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建知识点"""
        try:
            point = KnowledgePointCreate(**point_data)
            result = self.db.insert_data("knowledge_point", point.model_dump())
            return result[0] if result else None
        except Exception as e:
            return None
    
    def update_knowledge_point(self, point_id: int, point_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新知识点"""
        try:
            point = KnowledgePointUpdate(**point_data)
            result = self.db.update_data("knowledge_point", point.model_dump(exclude_unset=True), {"id": point_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def delete_knowledge_point(self, point_id: int) -> bool:
        """删除知识点"""
        try:
            result = self.db.delete_data("knowledge_point", {"id": point_id})
            return result is not None
        except Exception as e:
            return False
    
    # Questions API
    def get_questions(self) -> List[Dict[str, Any]]:
        """获取所有题目"""
        try:
            result = self.db.select_data("question")
            return result if result is not None else []
        except Exception as e:
            return []
    
    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取题目"""
        try:
            result = self.db.select_data("question", filters={"id": question_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def create_question(self, question_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建题目"""
        try:
            question = QuestionCreate(**question_data)
            result = self.db.insert_data("question", question.model_dump())
            return result[0] if result else None
        except Exception as e:
            return None
    
    def update_question(self, question_id: int, question_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新题目"""
        try:
            question = QuestionUpdate(**question_data)
            result = self.db.update_data("question", question.model_dump(exclude_unset=True), {"id": question_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def delete_question(self, question_id: int) -> bool:
        """删除题目"""
        try:
            result = self.db.delete_data("question", {"id": question_id})
            return result is not None
        except Exception as e:
            return False
    
    def create_questions_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """批量创建题目"""
        try:
            batch_request = BatchQuestionCreate(**batch_data)
            questions_data = batch_request.questions
            
            success_count = 0
            failed_count = 0
            errors = []
            
            for question_data in questions_data:
                try:
                    # 添加image_id到每个题目
                    question_dict = question_data.model_dump()
                    question_dict["image_id"] = batch_request.image_id
                    
                    result = self.db.insert_data("question", question_dict)
                    if result:
                        success_count += 1
                    else:
                        failed_count += 1
                        errors.append(f"Failed to create question: {question_dict.get('content', 'Unknown')}")
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Error creating question: {str(e)}")
            
            return {
                "success_count": success_count,
                "failed_count": failed_count,
                "errors": errors
            }
        except Exception as e:
            return {
                "success_count": 0,
                "failed_count": len(batch_data.get("questions", [])),
                "errors": [f"Batch creation failed: {str(e)}"]
            }
    
    # Question Knowledge Points API
    def get_question_knowledge_points(self) -> List[Dict[str, Any]]:
        """获取所有题目知识点关联"""
        try:
            result = self.db.select_data("question_knowledge_point")
            return result if result is not None else []
        except Exception as e:
            return []
    
    def get_question_knowledge_point(self, relation_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取题目知识点关联"""
        try:
            result = self.db.select_data("question_knowledge_point", filters={"id": relation_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def create_question_knowledge_point(self, relation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建题目知识点关联"""
        try:
            relation = QuestionKnowledgePointCreate(**relation_data)
            result = self.db.insert_data("question_knowledge_point", relation.model_dump())
            return result[0] if result else None
        except Exception as e:
            return None
    
    def update_question_knowledge_point(self, relation_id: int, relation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新题目知识点关联"""
        try:
            relation = QuestionKnowledgePointUpdate(**relation_data)
            result = self.db.update_data("question_knowledge_point", relation.model_dump(exclude_unset=True), {"id": relation_id})
            return result[0] if result else None
        except Exception as e:
            return None
    
    def delete_question_knowledge_point(self, relation_id: int) -> bool:
        """删除题目知识点关联"""
        try:
            result = self.db.delete_data("question_knowledge_point", {"id": relation_id})
            return result is not None
        except Exception as e:
            return False

# 创建全局API服务实例
api_service = APIService()

# 兼容性函数，模拟原来的API调用格式
def make_api_request(method: str, endpoint: str, data: Dict = None) -> Dict:
    """兼容原来的API请求格式"""
    try:
        # 解析endpoint
        parts = endpoint.split('/')
        resource = parts[0]
        
        if method == "GET":
            if len(parts) == 1:
                # 获取所有资源
                if resource == "users":
                    result = api_service.get_users()
                elif resource == "students":
                    result = api_service.get_students()
                elif resource == "exam_papers":
                    result = api_service.get_exam_papers()
                elif resource == "exam_paper_images":
                    result = api_service.get_exam_paper_images()
                elif resource == "knowledge_points":
                    result = api_service.get_knowledge_points()
                elif resource == "questions":
                    result = api_service.get_questions()
                elif resource == "question_knowledge_points":
                    result = api_service.get_question_knowledge_points()
                else:
                    return {"success": False, "error": f"Unknown resource: {resource}"}
                return {"success": True, "data": result}
            elif len(parts) == 2:
                # 根据ID获取单个资源
                resource_id = int(parts[1])
                if resource == "users":
                    result = api_service.get_user(resource_id)
                elif resource == "students":
                    result = api_service.get_student(resource_id)
                elif resource == "exam_papers":
                    result = api_service.get_exam_paper(resource_id)
                elif resource == "exam_paper_images":
                    result = api_service.get_exam_paper_image(resource_id)
                elif resource == "knowledge_points":
                    result = api_service.get_knowledge_point(resource_id)
                elif resource == "questions":
                    result = api_service.get_question(resource_id)
                elif resource == "question_knowledge_points":
                    result = api_service.get_question_knowledge_point(resource_id)
                else:
                    return {"success": False, "error": f"Unknown resource: {resource}"}
                
                if result is not None:
                    return {"success": True, "data": result}
                else:
                    return {"success": False, "error": "Resource not found"}
        
        elif method == "POST":
            if len(parts) == 1:
                # 创建资源
                if resource == "users":
                    result = api_service.create_user(data)
                elif resource == "students":
                    result = api_service.create_student(data)
                elif resource == "exam_papers":
                    result = api_service.create_exam_paper(data)
                elif resource == "exam_paper_images":
                    result = api_service.create_exam_paper_image(data)
                elif resource == "knowledge_points":
                    result = api_service.create_knowledge_point(data)
                elif resource == "questions":
                    result = api_service.create_question(data)
                elif resource == "question_knowledge_points":
                    result = api_service.create_question_knowledge_point(data)
                else:
                    return {"success": False, "error": f"Unknown resource: {resource}"}
                
                if result is not None:
                    return {"success": True, "data": result}
                else:
                    return {"success": False, "error": "Failed to create resource"}
            elif len(parts) == 2 and parts[1] == "batch" and resource == "questions":
                # 批量创建题目
                result = api_service.create_questions_batch(data)
                return {"success": True, "data": result}
        
        elif method == "PUT":
            if len(parts) == 2:
                # 更新资源
                resource_id = int(parts[1])
                if resource == "users":
                    result = api_service.update_user(resource_id, data)
                elif resource == "students":
                    result = api_service.update_student(resource_id, data)
                elif resource == "exam_papers":
                    result = api_service.update_exam_paper(resource_id, data)
                elif resource == "exam_paper_images":
                    result = api_service.update_exam_paper_image(resource_id, data)
                elif resource == "knowledge_points":
                    result = api_service.update_knowledge_point(resource_id, data)
                elif resource == "questions":
                    result = api_service.update_question(resource_id, data)
                elif resource == "question_knowledge_points":
                    result = api_service.update_question_knowledge_point(resource_id, data)
                else:
                    return {"success": False, "error": f"Unknown resource: {resource}"}
                
                if result is not None:
                    return {"success": True, "data": result}
                else:
                    return {"success": False, "error": "Failed to update resource"}
        
        elif method == "DELETE":
            if len(parts) == 2:
                # 删除资源
                resource_id = int(parts[1])
                if resource == "users":
                    result = api_service.delete_user(resource_id)
                elif resource == "students":
                    result = api_service.delete_student(resource_id)
                elif resource == "exam_papers":
                    result = api_service.delete_exam_paper(resource_id)
                elif resource == "exam_paper_images":
                    result = api_service.delete_exam_paper_image(resource_id)
                elif resource == "knowledge_points":
                    result = api_service.delete_knowledge_point(resource_id)
                elif resource == "questions":
                    result = api_service.delete_question(resource_id)
                elif resource == "question_knowledge_points":
                    result = api_service.delete_question_knowledge_point(resource_id)
                else:
                    return {"success": False, "error": f"Unknown resource: {resource}"}
                
                if result:
                    return {"success": True, "data": {"message": "Resource deleted successfully"}}
                else:
                    return {"success": False, "error": "Failed to delete resource"}
        
        return {"success": False, "error": f"Unsupported method or endpoint: {method} {endpoint}"}
    
    except Exception as e:
        return {"success": False, "error": f"API request failed: {str(e)}"}

# 兼容性函数，用于knowledge_points.py和question_knowledge_points.py
def api_request(method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
    """兼容原来的api_request格式"""
    result = make_api_request(method, endpoint, data)
    if result["success"]:
        return result["data"]
    else:
        return None