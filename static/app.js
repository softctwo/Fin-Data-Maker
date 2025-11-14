// 全局变量
let currentStep = 1;
let selectedTable = null;
let extractedFields = [];
let generatedDataCount = 0;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadDatabaseTypes();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 数据库类型变化
    document.getElementById('db-type').addEventListener('change', function() {
        const selectedType = this.value;
        updateFormByDatabaseType(selectedType);
    });

    // 连接表单提交
    document.getElementById('connection-form').addEventListener('submit', function(e) {
        e.preventDefault();
        testConnection();
    });
}

// 加载数据库类型
async function loadDatabaseTypes() {
    try {
        const response = await fetch('/api/databases/types');
        const result = await response.json();

        if (result.success) {
            const select = document.getElementById('db-type');
            result.data.forEach(db => {
                const option = document.createElement('option');
                option.value = db.value;
                option.textContent = db.label;
                option.dataset.port = db.default_port;
                select.appendChild(option);
            });
        }
    } catch (error) {
        showError('加载数据库类型失败: ' + error.message);
    }
}

// 根据数据库类型更新表单
function updateFormByDatabaseType(dbType) {
    const select = document.getElementById('db-type');
    const selectedOption = select.options[select.selectedIndex];
    const defaultPort = selectedOption.dataset.port;

    const hostGroup = document.getElementById('host-group');
    const portGroup = document.getElementById('port-group');
    const credentialsGroup = document.getElementById('credentials-group');

    if (dbType === 'sqlite') {
        // SQLite 只需要数据库文件路径
        hostGroup.classList.add('hidden');
        portGroup.classList.add('hidden');
        credentialsGroup.classList.add('hidden');
        document.getElementById('db-database').placeholder = '数据库文件路径';
    } else {
        // 其他数据库需要完整连接信息
        hostGroup.classList.remove('hidden');
        portGroup.classList.remove('hidden');
        credentialsGroup.classList.remove('hidden');
        document.getElementById('db-database').placeholder = '数据库名';

        // 设置默认端口
        if (defaultPort && defaultPort !== 'null') {
            document.getElementById('db-port').value = defaultPort;
        }
    }
}

// 测试数据库连接
async function testConnection() {
    const btn = document.querySelector('#connection-form button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="loading"></span> 连接中...';
    btn.disabled = true;

    const resultDiv = document.getElementById('connection-result');
    resultDiv.innerHTML = '';

    try {
        const dbType = document.getElementById('db-type').value;
        const data = {
            type: dbType,
            host: document.getElementById('db-host').value,
            port: parseInt(document.getElementById('db-port').value) || null,
            database: document.getElementById('db-database').value,
            username: document.getElementById('db-username').value,
            password: document.getElementById('db-password').value
        };

        const response = await fetch('/api/connection/test', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <i class="bi bi-check-circle"></i> ${result.message}
                </div>
            `;

            // 自动进入下一步
            setTimeout(() => {
                goToStep(2);
                loadTables();
            }, 1000);
        } else {
            resultDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-x-circle"></i> ${result.message}
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle"></i> 连接失败: ${error.message}
            </div>
        `;
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// 加载表列表
async function loadTables() {
    const listDiv = document.getElementById('tables-list');
    listDiv.innerHTML = '<div class="text-center"><span class="loading"></span> 加载表列表...</div>';

    try {
        const response = await fetch('/api/tables/list');
        const result = await response.json();

        if (result.success) {
            if (result.data.length === 0) {
                listDiv.innerHTML = '<div class="alert alert-info">未找到任何表</div>';
                return;
            }

            let html = '<div class="row">';
            result.data.forEach(table => {
                html += `
                    <div class="col-md-6">
                        <div class="table-info-card" onclick="selectTable('${table.table_name}', this)">
                            <h5><i class="bi bi-table"></i> ${table.table_name}</h5>
                            <div class="text-muted small">
                                <span><i class="bi bi-list-columns"></i> ${table.column_count} 字段</span>
                                <span class="ms-3"><i class="bi bi-file-earmark-text"></i> ${table.row_count} 行</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';

            listDiv.innerHTML = html;
        } else {
            listDiv.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        listDiv.innerHTML = `<div class="alert alert-danger">加载失败: ${error.message}</div>`;
    }
}

// 选择表
async function selectTable(tableName, element) {
    // 移除其他选中状态
    document.querySelectorAll('.table-info-card').forEach(card => {
        card.classList.remove('selected');
    });

    // 添加选中状态
    element.classList.add('selected');
    selectedTable = tableName;

    // 提取表结构
    await extractTableStructure(tableName);

    // 启用下一步按钮
    document.getElementById('btn-next-to-profile').disabled = false;
}

// 提取表结构
async function extractTableStructure(tableName) {
    const fieldsDiv = document.getElementById('table-fields');
    fieldsDiv.classList.remove('hidden');
    fieldsDiv.innerHTML = '<div class="text-center"><span class="loading"></span> 提取表结构...</div>';

    try {
        const response = await fetch('/api/table/extract', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({table_name: tableName})
        });

        const result = await response.json();

        if (result.success) {
            extractedFields = result.data.fields;

            let html = `
                <div class="alert alert-info">
                    <h5><i class="bi bi-info-circle"></i> 表信息</h5>
                    <p class="mb-1"><strong>表名:</strong> ${result.data.name}</p>
                    <p class="mb-1"><strong>字段数:</strong> ${result.data.field_count}</p>
                    ${result.data.primary_key ? `<p class="mb-0"><strong>主键:</strong> ${result.data.primary_key}</p>` : ''}
                </div>

                <h6>字段列表</h6>
                <div class="field-list">
                    <table class="table table-sm table-hover">
                        <thead>
                            <tr>
                                <th>字段名</th>
                                <th>类型</th>
                                <th>必填</th>
                                <th>唯一</th>
                                <th>描述</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            result.data.fields.forEach(field => {
                html += `
                    <tr>
                        <td><code>${field.name}</code></td>
                        <td><span class="badge bg-secondary">${field.type}</span></td>
                        <td>${field.required ? '<i class="bi bi-check-circle text-success"></i>' : ''}</td>
                        <td>${field.unique ? '<i class="bi bi-star text-warning"></i>' : ''}</td>
                        <td class="text-muted small">${field.description || '-'}</td>
                    </tr>
                `;
            });

            html += `
                        </tbody>
                    </table>
                </div>
            `;

            fieldsDiv.innerHTML = html;
        } else {
            fieldsDiv.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        fieldsDiv.innerHTML = `<div class="alert alert-danger">提取失败: ${error.message}</div>`;
    }
}

// 分析数据质量
async function analyzeDataQuality() {
    const resultsDiv = document.getElementById('profile-results');
    resultsDiv.innerHTML = '<div class="text-center"><span class="loading"></span> 分析数据质量中，请稍候...</div>';

    const sampleSize = parseInt(document.getElementById('sample-size').value);
    const strictness = document.getElementById('strictness').value;

    try {
        const response = await fetch('/api/table/profile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                sample_size: sampleSize,
                strictness: strictness
            })
        });

        const result = await response.json();

        if (result.success) {
            displayProfileResults(result.data);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">分析失败: ${error.message}</div>`;
    }
}

// 显示分析结果
function displayProfileResults(data) {
    const resultsDiv = document.getElementById('profile-results');

    let html = '<div class="alert alert-success"><i class="bi bi-check-circle"></i> 数据质量分析完成</div>';

    // 质量规则建议
    if (data.rules && data.rules.length > 0) {
        html += `
            <div class="card mb-3">
                <div class="card-header">
                    <h6 class="mb-0"><i class="bi bi-list-check"></i> 质量规则建议</h6>
                </div>
                <div class="card-body">
                    <ul class="mb-0">
                        ${data.rules.map(rule => `<li>${rule}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // 字段质量概况
    html += '<h6>字段质量概况</h6><div class="row">';

    let fieldCount = 0;
    for (const [fieldName, profile] of Object.entries(data.profiles)) {
        if (fieldCount >= 20) break; // 最多显示20个字段

        const completenessClass = profile.completeness_rate >= 0.95 ? 'quality-high' :
                                  profile.completeness_rate >= 0.80 ? 'quality-medium' : 'quality-low';
        const uniquenessClass = profile.uniqueness_rate >= 0.95 ? 'quality-high' :
                                profile.uniqueness_rate >= 0.80 ? 'quality-medium' : 'quality-low';

        html += `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title"><code>${fieldName}</code></h6>
                        <div class="mb-2">
                            <small class="text-muted">完整性:</small>
                            <span class="quality-badge ${completenessClass}">
                                ${(profile.completeness_rate * 100).toFixed(1)}%
                            </span>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted">唯一性:</small>
                            <span class="quality-badge ${uniquenessClass}">
                                ${(profile.uniqueness_rate * 100).toFixed(1)}%
                            </span>
                        </div>
                        ${profile.min_value !== null ? `
                            <div class="small text-muted">
                                范围: [${profile.min_value}, ${profile.max_value}]
                            </div>
                        ` : ''}
                        ${profile.min_length !== null ? `
                            <div class="small text-muted">
                                长度: [${profile.min_length}, ${profile.max_length}]
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        fieldCount++;
    }

    html += '</div>';
    resultsDiv.innerHTML = html;
}

// 生成数据
async function generateData() {
    const resultsDiv = document.getElementById('generation-results');
    resultsDiv.innerHTML = '<div class="text-center"><span class="loading"></span> 生成数据中，请稍候...</div>';

    const count = parseInt(document.getElementById('generate-count').value);
    const seed = parseInt(document.getElementById('random-seed').value);
    const validate = document.getElementById('validate-data').value === 'true';

    try {
        const response = await fetch('/api/data/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                count: count,
                seed: seed,
                validate: validate
            })
        });

        const result = await response.json();

        if (result.success) {
            generatedDataCount = result.data.count;
            displayGenerationResults(result.data);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${result.message}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">生成失败: ${error.message}</div>`;
    }
}

// 显示生成结果
function displayGenerationResults(data) {
    const resultsDiv = document.getElementById('generation-results');

    let html = `
        <div class="alert alert-success">
            <i class="bi bi-check-circle"></i> 成功生成 ${data.count} 条数据
        </div>
    `;

    // 验证报告
    if (data.report) {
        const report = data.report;
        html += `
            <div class="card mb-3">
                <div class="card-header">
                    <h6 class="mb-0"><i class="bi bi-clipboard-check"></i> 验证报告</h6>
                </div>
                <div class="card-body">
                    <div class="row text-center">
                        <div class="col-md-3">
                            <h4>${report.total_rows}</h4>
                            <small class="text-muted">总行数</small>
                        </div>
                        <div class="col-md-3">
                            <h4 class="text-success">${report.valid_rows}</h4>
                            <small class="text-muted">有效行数</small>
                        </div>
                        <div class="col-md-3">
                            <h4 class="text-danger">${report.error_count}</h4>
                            <small class="text-muted">错误数</small>
                        </div>
                        <div class="col-md-3">
                            <h4 class="text-warning">${report.warning_count}</h4>
                            <small class="text-muted">警告数</small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    resultsDiv.innerHTML = html;

    // 显示数据预览
    displayDataPreview(data.preview);

    // 显示导出选项
    displayExportSection();
}

// 显示数据预览
function displayDataPreview(previewData) {
    const previewDiv = document.getElementById('data-preview');
    previewDiv.classList.remove('hidden');

    if (!previewData || previewData.length === 0) {
        previewDiv.innerHTML = '<div class="alert alert-warning">无预览数据</div>';
        return;
    }

    const fields = Object.keys(previewData[0]);

    let html = `
        <h6>数据预览（前10条）</h6>
        <div class="table-responsive">
            <table class="table table-sm table-bordered data-preview-table">
                <thead class="table-light">
                    <tr>
                        ${fields.map(field => `<th>${field}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
    `;

    previewData.forEach(row => {
        html += '<tr>';
        fields.forEach(field => {
            let value = row[field];
            if (value === null) value = '<span class="text-muted">NULL</span>';
            else if (typeof value === 'string' && value.length > 50) {
                value = value.substring(0, 50) + '...';
            }
            html += `<td>${value}</td>`;
        });
        html += '</tr>';
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    previewDiv.innerHTML = html;
}

// 显示导出选项
function displayExportSection() {
    const exportDiv = document.getElementById('export-section');
    exportDiv.classList.remove('hidden');

    exportDiv.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h6 class="mb-0"><i class="bi bi-download"></i> 导出数据</h6>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4">
                        <button class="btn btn-primary w-100" onclick="exportData('csv')">
                            <i class="bi bi-file-earmark-spreadsheet"></i> 导出为 CSV
                        </button>
                    </div>
                    <div class="col-md-4">
                        <button class="btn btn-success w-100" onclick="exportData('excel')">
                            <i class="bi bi-file-earmark-excel"></i> 导出为 Excel
                        </button>
                    </div>
                    <div class="col-md-4">
                        <button class="btn btn-info w-100" onclick="exportData('json')">
                            <i class="bi bi-file-earmark-code"></i> 导出为 JSON
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 导出数据
async function exportData(format) {
    try {
        const response = await fetch('/api/data/export', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({format: format})
        });

        if (response.ok) {
            // 下载文件
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            // 从响应头获取文件名
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'data.' + format;
            if (contentDisposition) {
                const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showSuccess(`文件已下载: ${filename}`);
        } else {
            const result = await response.json();
            showError(result.message || '导出失败');
        }
    } catch (error) {
        showError('导出失败: ' + error.message);
    }
}

// 跳过分析
function skipAnalysis() {
    goToStep(4);
}

// 切换步骤
function goToStep(stepNumber) {
    // 隐藏所有步骤
    for (let i = 1; i <= 4; i++) {
        document.getElementById(`step-${i}`).classList.add('hidden');
        document.getElementById(`progress-step-${i}`).classList.remove('active', 'completed');
    }

    // 显示目标步骤
    document.getElementById(`step-${stepNumber}`).classList.remove('hidden');
    document.getElementById(`progress-step-${stepNumber}`).classList.add('active');

    // 标记已完成的步骤
    for (let i = 1; i < stepNumber; i++) {
        document.getElementById(`progress-step-${i}`).classList.add('completed');
    }

    currentStep = stepNumber;

    // 滚动到顶部
    window.scrollTo(0, 0);
}

// 重置所有
async function resetAll() {
    if (!confirm('确定要重新开始吗？这将清除所有当前数据。')) {
        return;
    }

    try {
        await fetch('/api/session/clear', {method: 'POST'});
    } catch (error) {
        console.error('清除会话失败:', error);
    }

    // 重置表单
    document.getElementById('connection-form').reset();
    document.getElementById('connection-result').innerHTML = '';
    document.getElementById('tables-list').innerHTML = '';
    document.getElementById('table-fields').classList.add('hidden');
    document.getElementById('profile-results').innerHTML = '';
    document.getElementById('generation-results').innerHTML = '';
    document.getElementById('data-preview').classList.add('hidden');
    document.getElementById('export-section').classList.add('hidden');

    // 重置变量
    selectedTable = null;
    extractedFields = [];
    generatedDataCount = 0;

    // 回到第一步
    goToStep(1);
}

// 辅助函数
function showSuccess(message) {
    alert(message); // 可以用更好的通知组件替代
}

function showError(message) {
    alert('错误: ' + message);
}
