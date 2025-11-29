import requests
from data_collector import YoutubeClient
from datetime import datetime
from typing import List, Dict


class MWSContentWriter:
    def __init__(self, mws_api_key: str):
        """
        Инициализация клиента для MWS Tables

        Args:
            mws_api_key: API ключ MWS Tables
        """
        self.mws_api_key = mws_api_key
        self.space_id = "dstEPg0bL9lD8jiDmt"  # datasheet ID из вашей ссылки
        self.view_id = "viwBSnap01TEa"  # view ID из вашей ссылки
        self.base_url = "https://tables.mws.ru/fusion/v1"

    def write_content_to_table(self, content_data: List[Dict]) -> Dict:
        """
        Записывает контент в таблицу MWS с правильными названиями полей
        """
        if not content_data:
            return {"error": "No data provided"}

        # Получаем актуальную структуру таблицы
        structure = self.get_table_structure()
        if 'error' in structure:
            return structure

        # Создаем маппинг по именам полей из таблицы
        field_mapping = {}
        for field in structure.get('data', {}).get('items', []):
            field_name = field.get('name', '')
            field_id = field['id']
            field_mapping[field_name] = field_id

        print("Найдены поля в таблице:", field_mapping)

        records = []
        for item in content_data:
            fields = {}

            # Маппим данные к полям таблицы
            # Ссылка
            if 'Ccылка' in field_mapping:
                fields[field_mapping['Ccылка']] = item['uri']

            # Платформа
            if 'Платформа' in field_mapping:
                fields[field_mapping['Платформа']] = self._detect_platform(item['uri'])

            # Текст
            if 'Текст' in field_mapping:
                fields[field_mapping['Текст']] = item.get('text', '')

            # Просмотры
            if 'Просмотры' in field_mapping:
                view_count = item.get('viewCount', 0)
                if isinstance(view_count, str):
                    view_count = int(view_count.replace(',', '')) if view_count.replace(',', '').isdigit() else 0
                fields[field_mapping['Просмотры']] = view_count

            # Лайки
            if 'Лайки' in field_mapping:
                fields[field_mapping['Лайки']] = item.get('likes', 0)

            # Комментарии
            if 'Комментарии' in field_mapping:
                fields[field_mapping['Комментарии']] = item.get('comment_count', 0)

            # Дата публикации
            if 'Дата публикации' in field_mapping:
                pub_date = item['publication_datetime']
                if isinstance(pub_date, datetime):
                    fields[field_mapping['Дата публикации']] = pub_date.isoformat()
                else:
                    fields[field_mapping['Дата публикации']] = datetime.now().isoformat()

            record = {"fields": fields}
            records.append(record)

        # Отправляем запрос
        endpoint = f"datasheets/{self.space_id}/records"
        headers = {
            "Authorization": f"Bearer {self.mws_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "records": records,
            "fieldKey": "id"
        }

        print(f"Отправляемые данные: {payload}")

        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                json=payload,
                timeout=30
            )

            print(f"Статус: {response.status_code}")
            print(f"Ответ: {response.text}")

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "records_processed": len(records),
                    "data": result
                }
            else:
                return {
                    "error": f"API Error {response.status_code}",
                    "details": response.text,
                    "status_code": response.status_code
                }

        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def read_table_data(self) -> Dict:
        """
        Читает данные из таблицы
        """
        endpoint = f"datasheets/{self.space_id}/records"
        headers = {
            "Authorization": f"Bearer {self.mws_api_key}",
            "Content-Type": "application/json"
        }

        params = {
            "viewId": self.view_id,
            "fieldKey": "id"
        }

        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API Error {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def get_table_structure(self) -> Dict:
        """
        Получает структуру таблицы (поля и их типы)
        """
        endpoint = f"datasheets/{self.space_id}/fields"
        headers = {
            "Authorization": f"Bearer {self.mws_api_key}",
            "Content-Type": "application/json"
        }

        params = {
            "viewId": self.view_id,
            "fieldKey": "id"
        }

        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API Error {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def _detect_platform(self, uri: str) -> str:
        """Определяет платформу по URI"""
        uri_lower = uri.lower()
        if 'youtube.com' in uri_lower or 'youtu.be' in uri_lower:
            return 'youtube'
        elif 'vk.com' in uri_lower:
            return 'vkontakte'
        elif 't.me' in uri_lower:
            return 'telegram'
        else:
            return 'other'

    def _detect_content_type(self, uri: str) -> str:
        """Определяет тип контента по URI"""
        uri_lower = uri.lower()
        if 'youtube.com' in uri_lower or 'youtu.be' in uri_lower:
            return 'video'
        elif 'vk.com/wall' in uri_lower:
            return 'post'
        elif 't.me' in uri_lower:
            return 'message'
        else:
            return 'unknown'


youtube = YoutubeClient("AIzaSyBB1nT_RE1FVHTvzcdF1e2FxBta7i7GFh8", "https://www.youtube.com/@pognalishow")

# Получение всех видео канала
videos_info = youtube.get_videos_info()

# # Получение комментариев для конкретного видео
# comments = youtube.get_comments_for_video("https://www.youtube.com/watch?v=UyaoBy3ETYI")

writer = MWSContentWriter('uskNd4PAf4ND1FODa1n4XQZ')
structure = writer.get_table_structure()
result = writer.write_content_to_table(videos_info[0])
table_data = writer.read_table_data()
print(table_data)