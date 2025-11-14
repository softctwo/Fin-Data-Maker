"""
数据导出器
支持CSV、JSON、Excel等格式
"""

import csv
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd


class DataExporter(ABC):
    """数据导出器基类"""

    @abstractmethod
    def export(self, data: List[Dict[str, Any]], file_path: str, **kwargs):
        """
        导出数据

        Args:
            data: 要导出的数据
            file_path: 输出文件路径
            **kwargs: 额外参数
        """
        pass


class CSVExporter(DataExporter):
    """CSV格式导出器"""

    def export(self, data: List[Dict[str, Any]], file_path: str, **kwargs):
        """
        导出为CSV格式

        Args:
            data: 要导出的数据
            file_path: 输出文件路径
            **kwargs: 额外参数（encoding, delimiter等）
        """
        if not data:
            return

        encoding = kwargs.get('encoding', 'utf-8-sig')  # 使用BOM以便Excel正确识别
        delimiter = kwargs.get('delimiter', ',')

        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', newline='', encoding=encoding) as f:
            # 获取所有字段名
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)

            writer.writeheader()
            writer.writerows(data)


class JSONExporter(DataExporter):
    """JSON格式导出器"""

    def export(self, data: List[Dict[str, Any]], file_path: str, **kwargs):
        """
        导出为JSON格式

        Args:
            data: 要导出的数据
            file_path: 输出文件路径
            **kwargs: 额外参数（indent, ensure_ascii等）
        """
        indent = kwargs.get('indent', 2)
        ensure_ascii = kwargs.get('ensure_ascii', False)

        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, default=str)


class ExcelExporter(DataExporter):
    """Excel格式导出器"""

    def export(self, data: List[Dict[str, Any]], file_path: str, **kwargs):
        """
        导出为Excel格式

        Args:
            data: 要导出的数据
            file_path: 输出文件路径
            **kwargs: 额外参数（sheet_name等）
        """
        if not data:
            return

        sheet_name = kwargs.get('sheet_name', 'Sheet1')

        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # 使用pandas导出
        df = pd.DataFrame(data)
        df.to_excel(file_path, sheet_name=sheet_name, index=False, engine='openpyxl')
