import streamlit as st
from supabase import create_client, Client

class SupabaseHandler:
    def __init__(self):
        """
        初始化 Supabase 客户端。
        """
        try:
            url: str = st.secrets["supabase"]["url"]
            key: str = st.secrets["supabase"]["key"]
        except KeyError as e:
            raise ValueError(f"Supabase 配置缺失: {e}。请检查 .streamlit/secrets.toml 文件配置。")
        
        if not url or not key:
            raise ValueError("Supabase URL 和 Key 不能为空。请检查 .streamlit/secrets.toml 文件配置。")
        self.client: Client = create_client(url, key)

    def select_data(self, table_name: str, columns: str = "*", filters: dict = None):
        """
        从指定的表中查询数据。

        :param table_name: 要查询的表名。
        :param columns: 要选择的列，默认为 "*" (所有列)。
        :param filters: 一个字典，用于过滤结果，例如 {"column_name": "value"}。
        :return: 查询结果的数据部分 (data) 或在出错时返回 None。
        """
        try:
            query = self.client.table(table_name).select(columns)
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value) # 使用 .eq() 进行精确匹配
            
            response = query.execute()
            return response.data
        except Exception as e:
            # 如果是表不存在的错误，只在非knowledge_point表时打印错误
            if "Could not find the table" in str(e) and table_name == "knowledge_point":
                # knowledge_point表可能不存在，这是正常情况
                return []
            print(f"查询数据时出错: {e}")
            return None

    def insert_data(self, table_name: str, data: dict):
        """
        向指定的表中插入单条数据。

        :param table_name: 目标表名。
        :param data: 要插入的数据，以字典形式提供。
        :return: 插入成功后的数据或在出错时返回 None。
        """
        try:
            # 创建数据副本，移除id字段以避免主键冲突
            insert_data = data.copy()
            if 'id' in insert_data:
                del insert_data['id']
            
            response = self.client.table(table_name).insert(insert_data).execute()
            return response.data
        except Exception as e:
            print(f"插入数据时出错: {e}")
            return None

    def update_data(self, table_name: str, data: dict, filters: dict):
        """
        更新指定表中的数据。

        :param table_name: 目标表名。
        :param data: 要更新的新数据。
        :param filters: 一个字典，用于定位要更新的行。
        :return: 更新成功后的数据或在出错时返回 None。
        """
        try:
            query = self.client.table(table_name).update(data)
            for column, value in filters.items():
                query = query.eq(column, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"更新数据时出错: {e}")
            return None

    def delete_data(self, table_name: str, filters: dict):
        """
        从指定表中删除数据。

        :param table_name: 目标表名。
        :param filters: 一个字典，用于定位要删除的行。
        :return: 删除成功后的数据或在出错时返回 None。
        """
        try:
            query = self.client.table(table_name).delete()
            for column, value in filters.items():
                query = query.eq(column, value)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"删除数据时出错: {e}")
            return None

# --- 如何使用这个类 ---
if __name__ == "__main__":
    # 1. 实例化处理器
    db_handler = SupabaseHandler()

    # 2. 插入一条新数据
    print("--- 插入数据 ---")
    new_country = {"name": "Python Land", "iso2": "PL"}
    inserted_data = db_handler.insert_data(table_name="countries", data=new_country)
    if inserted_data:
        print("插入成功:", inserted_data)
        country_id = inserted_data[0]['id']

    # 3. 查询所有数据
    print("\n--- 查询所有数据 ---")
    all_countries = db_handler.select_data(table_name="countries")
    if all_countries:
        print("查询结果:", all_countries)

    # 4. 根据条件查询特定数据
    print("\n--- 查询特定数据 ---")
    specific_country = db_handler.select_data(table_name="countries", filters={"name": "Python Land"})
    if specific_country:
        print("找到特定国家:", specific_country)

    # 5. 更新数据
    if inserted_data:
        print("\n--- 更新数据 ---")
        updated_info = {"name": "Advanced Python Land"}
        updated_data = db_handler.update_data(
            table_name="countries",
            data=updated_info,
            filters={"id": country_id}
        )
        if updated_data:
            print("更新成功:", updated_data)

    # 6. 删除数据
    if inserted_data:
        print("\n--- 删除数据 ---")
        deleted_data = db_handler.delete_data(
            table_name="countries",
            filters={"id": country_id}
        )
        if deleted_data:
            print("删除成功:", deleted_data)