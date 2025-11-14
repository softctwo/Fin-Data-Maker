#!/usr/bin/env python
"""
Flask Web应用
提供Web界面进行数据源连接、数据分析和测试数据生成
"""

from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
import os
import json
import traceback
from datetime import datetime
import tempfile

from src.datasource.db_connector import DatabaseConnector, DatabaseType
from src.datasource.metadata_extractor import MetadataExtractor
from src.datasource.data_profiler import DataProfiler
from src.core.app import DataMakerApp

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 生产环境应使用固定的密钥
CORS(app)

# 全局变量存储连接（生产环境应使用Redis等）
connections = {}
extractors = {}
profilers = {}


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/databases/types', methods=['GET'])
def get_database_types():
    """获取支持的数据库类型"""
    types = [
        {'value': 'mysql', 'label': 'MySQL', 'default_port': 3306},
        {'value': 'postgresql', 'label': 'PostgreSQL', 'default_port': 5432},
        {'value': 'oracle', 'label': 'Oracle', 'default_port': 1521},
        {'value': 'sqlserver', 'label': 'SQL Server', 'default_port': 1433},
        {'value': 'sqlite', 'label': 'SQLite', 'default_port': None},
    ]
    return jsonify({'success': True, 'data': types})


@app.route('/api/connection/test', methods=['POST'])
def test_connection():
    """测试数据库连接"""
    try:
        data = request.json
        db_type = DatabaseType(data['type'])

        connector = DatabaseConnector(
            db_type=db_type,
            host=data.get('host'),
            port=data.get('port'),
            database=data.get('database', ''),
            username=data.get('username'),
            password=data.get('password')
        )

        # 测试连接
        connector.connect()

        # 保存连接
        session_id = session.get('session_id', str(datetime.now().timestamp()))
        session['session_id'] = session_id
        connections[session_id] = connector
        extractors[session_id] = MetadataExtractor(connector)
        profilers[session_id] = DataProfiler(connector)

        return jsonify({
            'success': True,
            'message': '连接成功',
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'连接失败: {str(e)}'
        }), 400


@app.route('/api/tables/list', methods=['GET'])
def list_tables():
    """列出所有表"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in connections:
            return jsonify({
                'success': False,
                'message': '请先连接数据库'
            }), 400

        connector = connections[session_id]
        schema = request.args.get('schema')

        tables = connector.list_tables(schema)

        # 获取每个表的统计信息
        table_info = []
        extractor = extractors[session_id]
        for table_name in tables:
            try:
                stats = extractor.get_table_statistics(table_name, schema)
                table_info.append(stats)
            except:
                table_info.append({
                    'table_name': table_name,
                    'row_count': 0,
                    'column_count': 0
                })

        return jsonify({
            'success': True,
            'data': table_info
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/table/extract', methods=['POST'])
def extract_table():
    """提取表结构"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in extractors:
            return jsonify({
                'success': False,
                'message': '请先连接数据库'
            }), 400

        data = request.json
        table_name = data['table_name']
        schema = data.get('schema')

        extractor = extractors[session_id]
        table = extractor.extract_table(table_name, schema)

        # 保存表定义到session
        session['current_table'] = table.to_dict()

        return jsonify({
            'success': True,
            'data': {
                'name': table.name,
                'description': table.description,
                'primary_key': table.primary_key,
                'field_count': len(table.fields),
                'fields': [f.to_dict() for f in table.fields]
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/table/profile', methods=['POST'])
def profile_table():
    """分析表数据质量"""
    try:
        session_id = session.get('session_id')
        if not session_id or session_id not in profilers:
            return jsonify({
                'success': False,
                'message': '请先连接数据库'
            }), 400

        data = request.json
        sample_size = data.get('sample_size', 1000)

        # 获取当前表定义
        table_dict = session.get('current_table')
        if not table_dict:
            return jsonify({
                'success': False,
                'message': '请先提取表结构'
            }), 400

        from src.metadata.table import Table
        table = Table.from_dict(table_dict)

        # 分析数据质量
        profiler = profilers[session_id]
        profiles = profiler.profile_table(table, sample_size)

        # 转换为可序列化的格式
        profiles_data = {
            field_name: profile.to_dict()
            for field_name, profile in profiles.items()
        }

        # 生成质量规则建议
        strictness = data.get('strictness', 'medium')
        rules = profiler.generate_quality_rules(table, profiles, strictness)

        # 更新表定义
        updated_table = profiler.update_table_metadata(table, profiles)
        session['current_table'] = updated_table.to_dict()

        # 保存profiles到session
        session['profiles'] = profiles_data

        return jsonify({
            'success': True,
            'data': {
                'profiles': profiles_data,
                'rules': rules,
                'updated_fields': [f.to_dict() for f in updated_table.fields]
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data/generate', methods=['POST'])
def generate_data():
    """生成测试数据"""
    try:
        data = request.json
        count = data.get('count', 100)
        validate = data.get('validate', True)
        seed = data.get('seed', 42)

        # 获取当前表定义
        table_dict = session.get('current_table')
        if not table_dict:
            return jsonify({
                'success': False,
                'message': '请先提取表结构'
            }), 400

        from src.metadata.table import Table
        table = Table.from_dict(table_dict)

        # 生成数据
        app_instance = DataMakerApp(seed=seed)
        app_instance.add_table(table)

        generated_data, report = app_instance.generate_data(
            table.name,
            count=count,
            validate=validate
        )

        # 保存生成的数据到session
        session['generated_data'] = generated_data
        session['table_name'] = table.name

        # 验证报告
        report_data = None
        if report:
            report_data = {
                'total_rows': report.total_rows,
                'valid_rows': report.valid_rows,
                'error_count': report.get_error_count(),
                'warning_count': report.get_warning_count(),
                'violations': [v.to_dict() for v in report.violations[:20]]  # 只返回前20条
            }

        # 返回预览数据（前10条）
        preview_data = generated_data[:10]

        return jsonify({
            'success': True,
            'data': {
                'count': len(generated_data),
                'preview': preview_data,
                'report': report_data
            }
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data/export', methods=['POST'])
def export_data():
    """导出数据"""
    try:
        data = request.json
        format_type = data.get('format', 'csv')

        # 获取生成的数据
        generated_data = session.get('generated_data')
        table_name = session.get('table_name', 'data')

        if not generated_data:
            return jsonify({
                'success': False,
                'message': '没有可导出的数据'
            }), 400

        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format_type == 'csv':
            filename = f'{table_name}_{timestamp}.csv'
            filepath = os.path.join(temp_dir, filename)

            from src.output.exporter import CSVExporter
            exporter = CSVExporter()
            exporter.export(generated_data, filepath)

        elif format_type == 'json':
            filename = f'{table_name}_{timestamp}.json'
            filepath = os.path.join(temp_dir, filename)

            from src.output.exporter import JSONExporter
            exporter = JSONExporter()
            exporter.export(generated_data, filepath)

        elif format_type == 'excel':
            filename = f'{table_name}_{timestamp}.xlsx'
            filepath = os.path.join(temp_dir, filename)

            from src.output.exporter import ExcelExporter
            exporter = ExcelExporter()
            exporter.export(generated_data, filepath)

        else:
            return jsonify({
                'success': False,
                'message': f'不支持的格式: {format_type}'
            }), 400

        # 返回文件
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """清除会话"""
    try:
        session_id = session.get('session_id')

        # 断开连接
        if session_id and session_id in connections:
            connections[session_id].disconnect()
            del connections[session_id]
            del extractors[session_id]
            del profilers[session_id]

        # 清除session
        session.clear()

        return jsonify({
            'success': True,
            'message': '会话已清除'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # 确保模板目录存在
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    print("=" * 80)
    print("Fin-Data-Maker Web应用")
    print("=" * 80)
    print("\n访问地址: http://localhost:5000")
    print("\n按 Ctrl+C 停止服务器\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
