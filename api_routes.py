#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API 路由定义
实现所有数据表的 CRUD 操作
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from supabase_handler import SupabaseHandler
from models import (
    UserCreate, UserResponse,
    StudentCreate, StudentResponse,
    ExamPaperCreate, ExamPaperResponse,
    ExamPaperImageCreate, ExamPaperImageResponse,
    KnowledgePointCreate, KnowledgePointResponse,
    QuestionCreate, QuestionResponse,
    QuestionKnowledgePointCreate, QuestionKnowledgePointResponse,
    BatchQuestionCreate, BatchQuestionResponse
)

# 创建路由器
router = APIRouter()

# 获取数据库处理器实例
def get_db_handler():
    return SupabaseHandler()

# ==================== Users 表 CRUD ====================

@router.get("/users", response_model=List[UserResponse])
async def get_users(db: SupabaseHandler = Depends(get_db_handler)):
    """获取所有用户"""
    try:
        result = db.select_data("user")
        return result if result is not None else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """根据 ID 获取用户"""
    try:
        result = db.select_data("user", filters={"id": user_id})
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """创建新用户"""
    try:
        user_data = user.dict()
        # 将password转换为password_hash
        if 'password' in user_data:
            # 简单的密码哈希处理（实际项目中应使用bcrypt等安全哈希）
            import hashlib
            password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
            user_data['password_hash'] = password_hash
            del user_data['password']
        
        # 如果包含id字段，先检查是否已存在
        if 'id' in user_data and user_data['id'] is not None:
            existing = db.select_data("user", filters={"id": user_data['id']})
            if existing:
                raise HTTPException(status_code=400, detail=f"用户ID {user_data['id']} 已存在")
        
        result = db.insert_data("user", user_data)
        if not result:
            raise HTTPException(status_code=500, detail="创建用户失败")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """更新用户信息"""
    try:
        result = db.update_data("user", user.dict(), {"id": user_id})
        if not result:
            raise HTTPException(status_code=404, detail="用户不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """删除用户"""
    try:
        result = db.delete_data("user", {"id": user_id})
        return {"message": "用户删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Students 表 CRUD ====================

@router.get("/students", response_model=List[StudentResponse])
async def get_students(db: SupabaseHandler = Depends(get_db_handler)):
    """获取所有学生"""
    try:
        result = db.select_data("student")
        return result if result is not None else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """根据 ID 获取学生"""
    try:
        result = db.select_data("student", filters={"id": student_id})
        if not result:
            raise HTTPException(status_code=404, detail="学生不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/students", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """创建新学生"""
    try:
        student_data = student.dict()
        
        # 如果包含id字段，先检查是否已存在
        if 'id' in student_data and student_data['id'] is not None:
            existing = db.select_data("student", filters={"id": student_data['id']})
            if existing:
                raise HTTPException(status_code=400, detail=f"学生ID {student_data['id']} 已存在")
        
        result = db.insert_data("student", student_data)
        if not result:
            raise HTTPException(status_code=500, detail="创建学生失败")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student: StudentCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """更新学生信息"""
    try:
        result = db.update_data("student", student.dict(), {"id": student_id})
        if not result:
            raise HTTPException(status_code=404, detail="学生不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/students/{student_id}")
async def delete_student(student_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """删除学生"""
    try:
        result = db.delete_data("student", {"id": student_id})
        return {"message": "学生删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Exam Papers 表 CRUD ====================

@router.get("/exam_papers", response_model=List[ExamPaperResponse])
async def get_exam_papers(db: SupabaseHandler = Depends(get_db_handler)):
    """获取所有试卷"""
    try:
        result = db.select_data("exam_paper")
        return result if result is not None else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exam_papers/{paper_id}", response_model=ExamPaperResponse)
async def get_exam_paper(paper_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """根据 ID 获取试卷"""
    try:
        result = db.select_data("exam_paper", filters={"id": paper_id})
        if not result:
            raise HTTPException(status_code=404, detail="试卷不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exam_papers", response_model=ExamPaperResponse)
async def create_exam_paper(paper: ExamPaperCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """创建新试卷"""
    try:
        paper_data = paper.dict()
        # 如果包含id字段，先检查是否已存在
        if 'id' in paper_data and paper_data['id'] is not None:
            existing = db.select_data("exam_paper", filters={"id": paper_data['id']})
            if existing:
                raise HTTPException(status_code=400, detail=f"试卷ID {paper_data['id']} 已存在")
        
        result = db.insert_data("exam_paper", paper_data)
        if not result:
            raise HTTPException(status_code=500, detail="创建试卷失败")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/exam_papers/{paper_id}", response_model=ExamPaperResponse)
async def update_exam_paper(paper_id: int, paper: ExamPaperCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """更新试卷信息"""
    try:
        result = db.update_data("exam_paper", paper.dict(), {"id": paper_id})
        if not result:
            raise HTTPException(status_code=404, detail="试卷不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/exam_papers/{paper_id}")
async def delete_exam_paper(paper_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """删除试卷"""
    try:
        result = db.delete_data("exam_paper", {"id": paper_id})
        return {"message": "试卷删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Exam Paper Images 表 CRUD ====================

@router.get("/exam_paper_images", response_model=List[ExamPaperImageResponse])
async def get_exam_paper_images(db: SupabaseHandler = Depends(get_db_handler)):
    """获取所有试卷图片"""
    try:
        result = db.select_data("exam_paper_image")
        return result if result is not None else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exam_paper_images/{image_id}", response_model=ExamPaperImageResponse)
async def get_exam_paper_image(image_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """根据 ID 获取试卷图片"""
    try:
        result = db.select_data("exam_paper_image", filters={"id": image_id})
        if not result:
            raise HTTPException(status_code=404, detail="试卷图片不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exam_paper_images", response_model=ExamPaperImageResponse)
async def create_exam_paper_image(image: ExamPaperImageCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """创建新试卷图片"""
    try:
        image_data = image.dict()
        # 如果包含id字段，先检查是否已存在
        if 'id' in image_data and image_data['id'] is not None:
            existing = db.select_data("exam_paper_image", filters={"id": image_data['id']})
            if existing:
                raise HTTPException(status_code=400, detail=f"试卷图片ID {image_data['id']} 已存在")
        
        result = db.insert_data("exam_paper_image", image_data)
        if not result:
            raise HTTPException(status_code=500, detail="创建试卷图片失败")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/exam_paper_images/{image_id}", response_model=ExamPaperImageResponse)
async def update_exam_paper_image(image_id: int, image: ExamPaperImageCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """更新试卷图片信息"""
    try:
        result = db.update_data("exam_paper_image", image.dict(), {"id": image_id})
        if not result:
            raise HTTPException(status_code=404, detail="试卷图片不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/exam_paper_images/{image_id}")
async def delete_exam_paper_image(image_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """删除试卷图片"""
    try:
        result = db.delete_data("exam_paper_image", {"id": image_id})
        return {"message": "试卷图片删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Knowledge Points 表 CRUD ====================

@router.get("/knowledge_points", response_model=List[KnowledgePointResponse])
async def get_knowledge_points(db: SupabaseHandler = Depends(get_db_handler)):
    """获取所有知识点"""
    try:
        result = db.select_data("knowledge_point")
        return result if result is not None else []
    except Exception as e:
        # 如果表不存在，返回空数组
        return []

@router.get("/knowledge_points/{point_id}", response_model=KnowledgePointResponse)
async def get_knowledge_point(point_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """根据 ID 获取知识点"""
    try:
        result = db.select_data("knowledge_point", filters={"id": point_id})
        if not result:
            raise HTTPException(status_code=404, detail="知识点不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge_points", response_model=KnowledgePointResponse)
async def create_knowledge_point(point: KnowledgePointCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """创建新知识点"""
    try:
        point_data = point.dict()
        # 如果包含id字段，先检查是否已存在
        if 'id' in point_data and point_data['id'] is not None:
            existing = db.select_data("knowledge_point", filters={"id": point_data['id']})
            if existing:
                raise HTTPException(status_code=400, detail=f"知识点ID {point_data['id']} 已存在")
        
        result = db.insert_data("knowledge_point", point_data)
        if not result:
            raise HTTPException(status_code=500, detail="创建知识点失败")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/knowledge_points/{point_id}", response_model=KnowledgePointResponse)
async def update_knowledge_point(point_id: int, point: KnowledgePointCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """更新知识点信息"""
    try:
        result = db.update_data("knowledge_point", point.dict(), {"id": point_id})
        if not result:
            raise HTTPException(status_code=404, detail="知识点不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/knowledge_points/{point_id}")
async def delete_knowledge_point(point_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """删除知识点"""
    try:
        result = db.delete_data("knowledge_point", {"id": point_id})
        return {"message": "知识点删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Questions 表 CRUD ====================

@router.get("/questions", response_model=List[QuestionResponse])
async def get_questions(db: SupabaseHandler = Depends(get_db_handler)):
    """获取所有题目"""
    try:
        result = db.select_data("question")
        return result if result is not None else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """根据 ID 获取题目"""
    try:
        result = db.select_data("question", filters={"id": question_id})
        if not result:
            raise HTTPException(status_code=404, detail="题目不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions", response_model=QuestionResponse)
async def create_question(question: QuestionCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """创建新题目"""
    try:
        question_data = question.dict()
        # 如果包含id字段，先检查是否已存在
        if 'id' in question_data and question_data['id'] is not None:
            existing = db.select_data("question", filters={"id": question_data['id']})
            if existing:
                raise HTTPException(status_code=400, detail=f"题目ID {question_data['id']} 已存在")
        
        result = db.insert_data("question", question_data)
        if not result:
            raise HTTPException(status_code=500, detail="创建题目失败")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/questions/batch", response_model=BatchQuestionResponse)
async def create_questions_batch(batch_request: BatchQuestionCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """批量创建题目"""
    try:
        created_questions = []
        errors = []
        success_count = 0
        failed_count = 0
        
        for i, question_item in enumerate(batch_request.questions):
            try:
                # 构建单个题目数据
                question_data = {
                    "exam_paper_id": batch_request.exam_paper_id,
                    "student_id": batch_request.student_id,
                    "image_id": batch_request.image_id,
                    "content": question_item.content,
                    "is_correct": question_item.is_correct,
                    "remark": batch_request.remark
                }
                
                # 创建题目
                result = db.insert_data("question", question_data)
                if result:
                    created_questions.append(result[0])
                    success_count += 1
                else:
                    errors.append(f"题目 {i+1}: 创建失败")
                    failed_count += 1
                    
            except Exception as e:
                errors.append(f"题目 {i+1}: {str(e)}")
                failed_count += 1
        
        return BatchQuestionResponse(
            success_count=success_count,
            failed_count=failed_count,
            created_questions=created_questions,
            errors=errors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question: QuestionCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """更新题目信息"""
    try:
        result = db.update_data("question", question.dict(), {"id": question_id})
        if not result:
            raise HTTPException(status_code=404, detail="题目不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """删除题目"""
    try:
        result = db.delete_data("question", {"id": question_id})
        return {"message": "题目删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Question Knowledge Points 表 CRUD ====================

@router.get("/question_knowledge_points", response_model=List[QuestionKnowledgePointResponse])
async def get_question_knowledge_points(db: SupabaseHandler = Depends(get_db_handler)):
    """获取所有题目知识点关联"""
    try:
        result = db.select_data("question_knowledge_point")
        return result if result is not None else []
    except Exception as e:
        # 如果表不存在，返回空数组
        return []

@router.get("/question_knowledge_points/{relation_id}", response_model=QuestionKnowledgePointResponse)
async def get_question_knowledge_point(relation_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """根据 ID 获取题目知识点关联"""
    try:
        result = db.select_data("question_knowledge_point", filters={"id": relation_id})
        if not result:
            raise HTTPException(status_code=404, detail="题目知识点关联不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/question_knowledge_points", response_model=QuestionKnowledgePointResponse)
async def create_question_knowledge_point(relation: QuestionKnowledgePointCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """创建新题目知识点关联"""
    try:
        relation_data = relation.dict()
        # 如果包含id字段，先检查是否已存在
        if 'id' in relation_data and relation_data['id'] is not None:
            existing = db.select_data("question_knowledge_point", filters={"id": relation_data['id']})
            if existing:
                raise HTTPException(status_code=400, detail=f"题目知识点关联ID {relation_data['id']} 已存在")
        
        result = db.insert_data("question_knowledge_point", relation_data)
        if not result:
            raise HTTPException(status_code=500, detail="创建题目知识点关联失败")
        return result[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/question_knowledge_points/{relation_id}", response_model=QuestionKnowledgePointResponse)
async def update_question_knowledge_point(relation_id: int, relation: QuestionKnowledgePointCreate, db: SupabaseHandler = Depends(get_db_handler)):
    """更新题目知识点关联信息"""
    try:
        result = db.update_data("question_knowledge_point", relation.dict(), {"id": relation_id})
        if not result:
            raise HTTPException(status_code=404, detail="题目知识点关联不存在")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/question_knowledge_points/{relation_id}")
async def delete_question_knowledge_point(relation_id: int, db: SupabaseHandler = Depends(get_db_handler)):
    """删除题目知识点关联"""
    try:
        result = db.delete_data("question_knowledge_point", {"id": relation_id})
        return {"message": "题目知识点关联删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))