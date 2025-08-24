"""Pydantic models for API request/response validation."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# User models
class UserBase(BaseModel):
    username: str
    password_hash: str


class UserCreate(BaseModel):
    username: str
    password: str  # 原始密码，会被哈希处理


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None  # 原始密码，会被哈希处理


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: Optional[datetime] = None
    password_hash: Optional[str] = None  # 添加password_hash字段

    class Config:
        from_attributes = True


# Student models
class StudentBase(BaseModel):
    user_id: Optional[int] = None  # 可选，因为可能先创建学生再关联用户
    name: str


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


# Exam Paper models
class ExamPaperBase(BaseModel):
    student_id: int
    title: Optional[str] = None
    description: Optional[str] = None


class ExamPaperCreate(ExamPaperBase):
    pass


class ExamPaperUpdate(BaseModel):
    student_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class ExamPaperResponse(BaseModel):
    id: int
    student_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    created_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# Exam Paper Image models
class ExamPaperImageBase(BaseModel):
    exam_paper_id: int
    image_url: str
    upload_order: Optional[int] = None


class ExamPaperImageCreate(ExamPaperImageBase):
    pass


class ExamPaperImageUpdate(BaseModel):
    exam_paper_id: Optional[int] = None
    image_url: Optional[str] = None
    upload_order: Optional[int] = None


class ExamPaperImageResponse(BaseModel):
    id: int
    exam_paper_id: int
    image_url: str
    upload_order: Optional[int] = None

    class Config:
        from_attributes = True


# Knowledge Point models
class KnowledgePointBase(BaseModel):
    name: str


class KnowledgePointCreate(KnowledgePointBase):
    pass


class KnowledgePointUpdate(BaseModel):
    name: Optional[str] = None


class KnowledgePointResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# Question models
class QuestionBase(BaseModel):
    exam_paper_id: int
    image_id: int
    student_id: int
    content: Optional[str] = None
    is_correct: Optional[bool] = None
    remark: Optional[str] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    exam_paper_id: Optional[int] = None
    image_id: Optional[int] = None
    student_id: Optional[int] = None
    content: Optional[str] = None
    is_correct: Optional[bool] = None
    remark: Optional[str] = None


class QuestionResponse(BaseModel):
    id: int
    exam_paper_id: int
    image_id: int
    student_id: int
    content: Optional[str] = None
    is_correct: Optional[bool] = None
    remark: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# Question Knowledge Point models
class QuestionKnowledgePointBase(BaseModel):
    question_id: int
    knowledge_point_id: int


class QuestionKnowledgePointCreate(QuestionKnowledgePointBase):
    pass


class QuestionKnowledgePointUpdate(BaseModel):
    question_id: Optional[int] = None
    knowledge_point_id: Optional[int] = None


class QuestionKnowledgePointResponse(BaseModel):
    id: int
    question_id: int
    knowledge_point_id: int
    created_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# Batch Question models
class BatchQuestionItem(BaseModel):
    """批量创建题目中的单个题目数据"""
    content: str
    is_correct: bool


class BatchQuestionCreate(BaseModel):
    """批量创建题目的请求模型"""
    exam_paper_id: int
    student_id: int
    image_id: Optional[int] = None
    remark: Optional[str] = None
    questions: List[BatchQuestionItem]


class BatchQuestionResponse(BaseModel):
    """批量创建题目的响应模型"""
    success_count: int
    failed_count: int
    created_questions: List[QuestionResponse]
    errors: List[str]