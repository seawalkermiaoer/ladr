#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯云COS上传工具
用于试卷图片的上传、删除和管理
"""

import os
import io
import uuid
import time
from datetime import datetime
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from PIL import Image
import streamlit as st


class ExamPaperCOSManager:
    """试卷图片COS管理器"""
    
    def __init__(self, secret_id=None, secret_key=None, region='ap-beijing', bucket_name=None):
        """
        初始化COS管理器
        
        Args:
            secret_id: 腾讯云SecretId，如果为None则从streamlit secrets获取
            secret_key: 腾讯云SecretKey，如果为None则从streamlit secrets获取
            region: COS地域
            bucket_name: 存储桶名称
        """
        # 从streamlit secrets获取配置
        if secret_id is None or secret_key is None:
            try:
                secret_id = st.secrets['oss']['secret_id']
                secret_key = st.secrets['oss']['secret_key']
                # 如果没有指定region和bucket_name，从secrets获取
                if region == 'ap-beijing':  # 默认值
                    region = st.secrets['oss'].get('region', 'ap-beijing')
                if bucket_name is None:
                    bucket_name = st.secrets['oss'].get('bucket_name', 'exam-papers-ladr')
            except Exception as e:
                raise ValueError(f"无法获取COS配置: {e}")
        
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.bucket_name = bucket_name or 'exam-papers-ladr'  # 默认存储桶名称
        
        # 配置COS客户端
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key,
            Token=None,
            Scheme='https'
        )
        self.client = CosS3Client(config)
    
    def upload_exam_paper_image(self, image_file, exam_paper_id, image_index=None):
        """
        上传试卷图片
        
        Args:
            image_file: 图片文件对象或bytes数据
            exam_paper_id: 试卷ID
            image_index: 图片索引（可选）
            
        Returns:
            dict: 上传结果
        """
        try:
            # 生成唯一的文件名
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            
            if image_index is not None:
                filename = f"exam_papers/{exam_paper_id}/page_{image_index}_{timestamp}_{unique_id}.jpg"
            else:
                filename = f"exam_papers/{exam_paper_id}/{timestamp}_{unique_id}.jpg"
            
            # 处理图片数据
            if hasattr(image_file, 'read'):
                image_data = image_file.read()
                image_file.seek(0)  # 重置文件指针
            else:
                image_data = image_file
            
            # 上传到COS
            response = self.client.put_object(
                Bucket=self.bucket_name,
                Body=image_data,
                Key=filename,
                ContentType='image/jpeg'
            )
            
            # 构建访问URL
            file_url = f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{filename}"
            
            return {
                'success': True,
                'url': file_url,
                'filename': filename,
                'etag': response['ETag'],
                'size': len(image_data),
                'message': '上传成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'url': None,
                'error': str(e),
                'message': f'上传失败: {str(e)}'
            }
    
    def upload_image(self, file_data, filename=None):
        """
        通用图片上传方法
        
        Args:
            file_data: 图片文件数据（bytes）
            filename: 自定义文件名（可选）
            
        Returns:
            dict: 上传结果
        """
        try:
            # 生成文件名
            if filename is None:
                timestamp = int(time.time())
                unique_id = str(uuid.uuid4())[:8]
                filename = f"uploads/{timestamp}_{unique_id}.jpg"
            else:
                # 确保文件名有正确的路径前缀
                if not filename.startswith('uploads/'):
                    filename = f"uploads/{filename}"
            
            # 上传到COS
            response = self.client.put_object(
                Bucket=self.bucket_name,
                Body=file_data,
                Key=filename,
                ContentType='image/jpeg'
            )
            
            # 构建访问URL
            file_url = f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{filename}"
            
            return {
                'success': True,
                'filename': filename,
                'cos_path': filename,
                'url': file_url,  # 修改字段名以匹配exam_papers.py中的使用
                'file_url': file_url,  # 保留原字段名以兼容其他代码
                'upload_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, filename):
        """
        删除文件
        
        Args:
            filename: 要删除的文件名
            
        Returns:
            dict: 删除结果
        """
        try:
            # 确保文件名有正确的路径前缀
            if not filename.startswith('uploads/') and not filename.startswith('exam_papers/'):
                filename = f"uploads/{filename}"
            
            response = self.client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            
            return {
                'success': True,
                'filename': filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_files(self, prefix='uploads/'):
        """
        列出文件
        
        Args:
            prefix: 文件路径前缀
            
        Returns:
            list: 文件列表
        """
        try:
            response = self.client.list_objects(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return files
            
        except Exception as e:
            print(f"列出文件失败: {e}")
            return []
    
    def get_file_url(self, filename):
        """
        获取文件访问URL
        
        Args:
            filename: 文件名
            
        Returns:
            str: 文件URL
        """
        return f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{filename}"
    
    def delete_exam_paper_image(self, filename):
        """
        删除试卷图片
        
        Args:
            filename: 图片文件名
            
        Returns:
            dict: 删除结果
        """
        try:
            response = self.client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            
            return {
                'success': True,
                'filename': filename
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_exam_paper_images(self, exam_paper_id):
        """
        删除指定试卷的所有图片
        
        Args:
            filename: COS中的文件名
            
        Returns:
            dict: 删除结果
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            return {
                'success': True,
                'message': '删除成功'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'删除失败: {str(e)}'
            }
    
    def delete_exam_paper_images(self, exam_paper_id):
        """
        删除试卷的所有图片
        
        Args:
            exam_paper_id: 试卷ID
            
        Returns:
            dict: 删除结果
        """
        try:
            # 列出该试卷的所有图片
            prefix = f"exam_papers/{exam_paper_id}/"
            response = self.client.list_objects(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            deleted_count = 0
            if 'Contents' in response:
                for obj in response['Contents']:
                    delete_result = self.delete_exam_paper_image(obj['Key'])
                    if delete_result['success']:
                        deleted_count += 1
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'message': f'成功删除 {deleted_count} 个图片文件'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'批量删除失败: {str(e)}'
            }
    
    def list_exam_paper_images(self, exam_paper_id):
        """
        列出试卷的所有图片
        
        Args:
            exam_paper_id: 试卷ID
            
        Returns:
            list: 图片文件列表
        """
        try:
            prefix = f"exam_papers/{exam_paper_id}/"
            response = self.client.list_objects(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            images = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    images.append({
                        'filename': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'url': f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{obj['Key']}"
                    })
            
            return images
            
        except Exception as e:
            print(f"列出图片失败: {str(e)}")
            return []
    
    def get_image_url(self, filename):
        """
        获取图片的访问URL
        
        Args:
            filename: COS中的文件名
            
        Returns:
            str: 图片URL
        """
        return f"https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{filename}"
    
    def get_presigned_url(self, filename, expires_in=3600):
        """
        生成预签名URL，用于解决跨域访问问题
        
        Args:
            filename: COS中的文件名
            expires_in: URL有效期（秒），默认1小时
            
        Returns:
            str: 预签名URL
        """
        try:
            # 生成预签名URL
            presigned_url = self.client.get_presigned_url(
                Method='GET',
                Bucket=self.bucket_name,
                Key=filename,
                Expired=expires_in
            )
            return presigned_url
        except Exception as e:
            print(f"生成预签名URL失败: {e}")
            # 如果生成预签名URL失败，返回普通URL作为备选
            return self.get_image_url(filename)
    
    def get_safe_image_url(self, filename, use_presigned=True, expires_in=3600):
        """
        获取安全的图片访问URL，优先使用预签名URL
        
        Args:
            filename: COS中的文件名
            use_presigned: 是否使用预签名URL，默认True
            expires_in: 预签名URL有效期（秒），默认1小时
            
        Returns:
            str: 安全的图片URL
        """
        if use_presigned:
            return self.get_presigned_url(filename, expires_in)
        else:
            return self.get_image_url(filename)
    
    def check_bucket_exists(self):
        """
        检查存储桶是否存在
        
        Returns:
            bool: 存储桶是否存在
        """
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception:
            return False
    
    def get_bucket_info(self):
        """
        获取存储桶信息
        
        Returns:
            dict: 存储桶信息
        """
        try:
            if not self.check_bucket_exists():
                return {
                    'exists': False,
                    'message': '存储桶不存在'
                }
            
            # 获取存储桶中的文件统计
            response = self.client.list_objects(
                Bucket=self.bucket_name,
                Prefix='exam_papers/'
            )
            
            file_count = 0
            total_size = 0
            if 'Contents' in response:
                file_count = len(response['Contents'])
                total_size = sum(obj['Size'] for obj in response['Contents'])
            
            return {
                'exists': True,
                'bucket_name': self.bucket_name,
                'region': self.region,
                'file_count': file_count,
                'total_size': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2)
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': str(e),
                'message': f'获取存储桶信息失败: {str(e)}'
            }


def create_cos_manager():
    """
    创建COS管理器实例
    
    Returns:
        ExamPaperCOSManager: COS管理器实例
    """
    try:
        return ExamPaperCOSManager()
    except Exception as e:
        st.error(f"初始化COS管理器失败: {e}")
        return None


# 使用示例
if __name__ == '__main__':
    print("腾讯云COS试卷图片管理工具")
    print("请在Streamlit应用中使用此模块")