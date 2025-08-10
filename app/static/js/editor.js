/**
 * 编辑器主逻辑
 * 处理Prompt编辑的所有交互功能
 */

// 全局变量
let editor = null; // CodeMirror实例
let currentPromptId = null; // 当前编辑的Prompt ID
let autoSaveTimer = null; // 自动保存定时器
let hasUnsavedChanges = false; // 是否有未保存的更改
let currentTags = []; // 当前选中的标签
let allTags = []; // 所有可用标签

/**
 * 页面初始化函数（会被layout.html调用）
 */
function initPage() {
    // 获取URL中的Prompt ID
    const pathParts = window.location.pathname.split('/');
    currentPromptId = pathParts[pathParts.length - 1];
    
    // 初始化编辑器
    initializeEditor();
    
    // 加载标签
    loadTags();
    
    // 如果是编辑模式，加载Prompt数据
    if (currentPromptId !== 'new') {
        loadPrompt(currentPromptId);
    }
    
    // 绑定事件
    bindEvents();
    
    // 设置快捷键
    setupKeyboardShortcuts();
}

// 兼容直接访问（不通过layout）
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        // 如果没有通过layout.html，直接初始化
        if (typeof initPage === 'function' && !window.layoutInitialized) {
            // 使用统一的认证检查
            if (window.AuthUtils && !window.AuthUtils.initAuthCheck()) {
                return; // 认证失败，已重定向
            }
            initPage();
        }
    });
}

/**
 * 初始化CodeMirror编辑器
 */
function initializeEditor() {
    const textarea = document.getElementById('promptEditor');
    
    editor = CodeMirror.fromTextArea(textarea, {
        mode: 'markdown',
        theme: 'elegant',
        lineNumbers: true,
        lineWrapping: true,
        autofocus: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        extraKeys: {
            'Tab': (cm) => cm.execCommand('indentMore'),
            'Shift-Tab': (cm) => cm.execCommand('indentLess')
        }
    });
    
    // 监听内容变化
    editor.on('change', () => {
        hasUnsavedChanges = true;
        updateWordCount();
        triggerAutoSave();
    });
    
    // 初始化字数统计
    updateWordCount();
}

/**
 * 更新字数统计
 */
function updateWordCount() {
    const content = editor.getValue();
    const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
    const charCount = content.length;
    
    document.getElementById('wordCount').textContent = `${wordCount} 字`;
    document.getElementById('charCount').textContent = `${charCount} 字符`;
}

/**
 * 触发自动保存
 */
function triggerAutoSave() {
    // 清除之前的定时器
    if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
    }
    
    // 更新保存状态为"正在编辑"
    updateSaveStatus('editing');
    
    // 3秒后自动保存
    autoSaveTimer = setTimeout(() => {
        if (hasUnsavedChanges && currentPromptId !== 'new') {
            autoSave();
        }
    }, 3000);
}

/**
 * 自动保存
 */
async function autoSave() {
    if (!currentPromptId || currentPromptId === 'new') return;
    
    updateSaveStatus('saving');
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/v1/prompts/${currentPromptId}/autosave`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: document.getElementById('titleInput').value,
                content: editor.getValue()
            })
        });
        
        if (response.ok) {
            hasUnsavedChanges = false;
            updateSaveStatus('saved');
        } else {
            updateSaveStatus('error');
        }
    } catch (error) {
        console.error('自动保存失败:', error);
        updateSaveStatus('error');
    }
}

/**
 * 更新保存状态显示
 */
function updateSaveStatus(status) {
    const saveStatus = document.getElementById('saveStatus');
    const statusText = saveStatus.querySelector('.status-text');
    
    saveStatus.className = 'save-status';
    
    switch (status) {
        case 'editing':
            statusText.textContent = '正在编辑...';
            break;
        case 'saving':
            saveStatus.classList.add('saving');
            statusText.textContent = '保存中...';
            break;
        case 'saved':
            statusText.textContent = '已保存';
            break;
        case 'error':
            saveStatus.classList.add('error');
            statusText.textContent = '保存失败';
            break;
    }
}

/**
 * 加载Prompt数据
 */
async function loadPrompt(promptId) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/v1/prompts/${promptId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const prompt = data.data;
            
            // 填充数据
            document.getElementById('titleInput').value = prompt.title || '';
            document.getElementById('descriptionInput').value = prompt.description || '';
            editor.setValue(prompt.content || '');
            
            // 显示版本信息
            if (prompt.current_version) {
                document.getElementById('versionInfo').textContent = 
                    `版本 ${prompt.current_version.version_number}`;
            }
            
            // 加载标签
            if (prompt.tags) {
                currentTags = prompt.tags;
                renderSelectedTags();
            }
            
            // 重置保存状态
            hasUnsavedChanges = false;
            updateSaveStatus('saved');
        } else if (response.status === 404) {
            alert('Prompt不存在');
            window.location.href = '/home';
        }
    } catch (error) {
        console.error('加载Prompt失败:', error);
        alert('加载失败，请重试');
    }
}

/**
 * 加载所有标签
 */
async function loadTags() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/v1/tags', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            allTags = data.data;
            renderTagSelector();
        }
    } catch (error) {
        console.error('加载标签失败:', error);
    }
}

/**
 * 渲染已选标签
 */
function renderSelectedTags() {
    const container = document.getElementById('selectedTags');
    container.innerHTML = '';
    
    currentTags.forEach(tag => {
        const tagEl = document.createElement('span');
        tagEl.className = 'tag';
        tagEl.style.borderColor = tag.color;
        tagEl.innerHTML = `
            ${tag.name}
            <span class="remove-icon">×</span>
        `;
        
        tagEl.addEventListener('click', () => {
            removeTag(tag.id);
        });
        
        container.appendChild(tagEl);
    });
}

/**
 * 渲染标签选择器
 */
function renderTagSelector() {
    const sceneContainer = document.getElementById('sceneTags');
    const modelContainer = document.getElementById('modelTags');
    const typeContainer = document.getElementById('typeTags');
    
    // 清空容器
    sceneContainer.innerHTML = '';
    modelContainer.innerHTML = '';
    typeContainer.innerHTML = '';
    
    // 按分类渲染标签
    allTags.forEach(tag => {
        const tagEl = document.createElement('span');
        tagEl.className = 'tag-option';
        tagEl.textContent = tag.name;
        tagEl.dataset.tagId = tag.id;
        tagEl.style.borderColor = tag.color;
        
        // 检查是否已选中
        if (currentTags.some(t => t.id === tag.id)) {
            tagEl.classList.add('selected');
        }
        
        tagEl.addEventListener('click', () => {
            toggleTag(tag);
        });
        
        // 根据分类添加到对应容器
        switch (tag.category) {
            case 'scene':
                sceneContainer.appendChild(tagEl);
                break;
            case 'model':
                modelContainer.appendChild(tagEl);
                break;
            case 'type':
                typeContainer.appendChild(tagEl);
                break;
            default:
                typeContainer.appendChild(tagEl);
        }
    });
}

/**
 * 切换标签选中状态
 */
function toggleTag(tag) {
    const index = currentTags.findIndex(t => t.id === tag.id);
    
    if (index > -1) {
        currentTags.splice(index, 1);
    } else {
        currentTags.push(tag);
    }
    
    renderSelectedTags();
    renderTagSelector();
    hasUnsavedChanges = true;
}

/**
 * 移除标签
 */
function removeTag(tagId) {
    currentTags = currentTags.filter(t => t.id !== tagId);
    renderSelectedTags();
    renderTagSelector();
    hasUnsavedChanges = true;
}

/**
 * 保存Prompt
 */
async function savePrompt() {
    const title = document.getElementById('titleInput').value.trim();
    const content = editor.getValue().trim();
    const description = document.getElementById('descriptionInput').value.trim();
    
    if (!title) {
        alert('请输入标题');
        return;
    }
    
    if (!content) {
        alert('请输入内容');
        return;
    }
    
    // 更新保存按钮状态
    const saveBtn = document.getElementById('saveBtn');
    const saveBtnText = saveBtn.innerHTML;
    saveBtn.classList.add('saving');
    saveBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
            <path d="M21 12a9 9 0 11-6.219-8.56"/>
        </svg>
        保存中...
    `;
    
    updateSaveStatus('saving');
    
    try {
        const token = localStorage.getItem('token');
        const tagIds = currentTags.map(t => t.id);
        
        let response;
        
        if (currentPromptId === 'new') {
            // 创建新Prompt
            response = await fetch('/api/v1/prompts', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    content,
                    description,
                    tags: tagIds
                })
            });
        } else {
            // 更新已有Prompt
            response = await fetch(`/api/v1/prompts/${currentPromptId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    content,
                    description,
                    tags: tagIds,
                    change_summary: '手动保存'
                })
            });
        }
        
        if (response.ok) {
            const data = await response.json();
            
            if (currentPromptId === 'new') {
                // 新建成功后跳转到编辑页面
                currentPromptId = data.data.id;
                window.history.replaceState({}, '', `/editor/${currentPromptId}`);
            }
            
            hasUnsavedChanges = false;
            updateSaveStatus('saved');
            
            // 更新版本号
            const versionCount = data.data.version_count || 1;
            document.getElementById('versionInfo').textContent = `版本 ${versionCount}`;
            
            // 恢复保存按钮状态
            saveBtn.classList.remove('saving');
            saveBtn.innerHTML = saveBtnText;
        } else {
            updateSaveStatus('error');
            alert('保存失败，请重试');
            // 恢复保存按钮状态
            saveBtn.classList.remove('saving');
            saveBtn.innerHTML = saveBtnText;
        }
    } catch (error) {
        console.error('保存失败:', error);
        updateSaveStatus('error');
        alert('保存失败，请检查网络连接');
        // 恢复保存按钮状态
        saveBtn.classList.remove('saving');
        saveBtn.innerHTML = saveBtnText;
    }
}

/**
 * 测试Prompt
 */
async function testPrompt() {
    const content = editor.getValue().trim();
    if (!content) {
        alert('请先输入Prompt内容');
        return;
    }
    
    // 显示测试面板
    const testPanel = document.getElementById('testPanel');
    testPanel.classList.add('active');
    
    // 清空之前的结果
    document.getElementById('testResult').style.display = 'none';
}

/**
 * 运行测试
 */
async function runTest() {
    const model = document.querySelector('input[name="model"]:checked').value;
    const temperature = parseFloat(document.getElementById('temperatureSlider').value);
    const testInput = document.getElementById('testInput').value;
    const promptContent = editor.getValue();
    
    const runBtn = document.getElementById('runTestBtn');
    const btnText = runBtn.querySelector('.btn-text');
    const spinner = runBtn.querySelector('.loading-spinner');
    
    // 显示加载状态
    runBtn.disabled = true;
    btnText.textContent = '测试中...';
    spinner.style.display = 'inline-block';
    
    try {
        const token = localStorage.getItem('token');
        
        // 如果是新建Prompt且未保存，提醒用户先保存
        if (currentPromptId === 'new') {
            alert('请先保存Prompt再进行测试');
            runBtn.disabled = false;
            btnText.textContent = '运行测试';
            spinner.style.display = 'none';
            return;
        }
        
        const response = await fetch(`/api/v1/prompts/${currentPromptId}/test`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model,
                input: testInput,
                parameters: {
                    temperature,
                    max_tokens: 1000
                }
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            displayTestResult(data.data);
        } else {
            alert('测试失败，请稍后重试');
        }
    } catch (error) {
        console.error('测试失败:', error);
        alert('测试失败，请检查网络连接');
    } finally {
        // 恢复按钮状态
        runBtn.disabled = false;
        btnText.textContent = '运行测试';
        spinner.style.display = 'none';
    }
}

/**
 * 显示测试结果
 */
function displayTestResult(result) {
    const resultContainer = document.getElementById('testResult');
    
    document.getElementById('resultModel').textContent = result.model;
    document.getElementById('resultTime').textContent = `${result.response_time}s`;
    document.getElementById('resultTokens').textContent = 
        `${result.tokens.input + result.tokens.output} tokens`;
    document.getElementById('resultContent').textContent = result.output;
    
    resultContainer.style.display = 'block';
}

/**
 * 复制测试结果
 */
function copyTestResult() {
    const content = document.getElementById('resultContent').textContent;
    
    navigator.clipboard.writeText(content).then(() => {
        const btn = document.getElementById('copyResultBtn');
        const originalText = btn.textContent;
        btn.textContent = '已复制！';
        
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('复制失败:', err);
        alert('复制失败，请手动复制');
    });
}

/**
 * 显示版本历史
 */
async function showVersionHistory() {
    if (currentPromptId === 'new') {
        alert('新建的Prompt还没有版本历史');
        return;
    }
    
    const historyPanel = document.getElementById('historyPanel');
    historyPanel.classList.add('active');
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/v1/prompts/${currentPromptId}/versions`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderVersionList(data.data.items);
        }
    } catch (error) {
        console.error('加载版本历史失败:', error);
    }
}

/**
 * 渲染版本列表
 */
function renderVersionList(versions) {
    const container = document.getElementById('versionList');
    container.innerHTML = '';
    
    versions.forEach(version => {
        const versionEl = document.createElement('div');
        versionEl.className = 'version-item';
        versionEl.innerHTML = `
            <div class="version-header">
                <span class="version-number">版本 ${version.version_number}</span>
                <span class="version-date">${formatDate(version.created_at)}</span>
            </div>
            <div class="version-summary">${version.change_summary || '无摘要'}</div>
            <div class="version-author">修改者: ${version.author.username}</div>
        `;
        
        versionEl.addEventListener('click', () => {
            loadVersion(version.id);
        });
        
        container.appendChild(versionEl);
    });
}

/**
 * 加载特定版本
 */
async function loadVersion(versionId) {
    if (!confirm('加载历史版本将覆盖当前内容，确定继续？')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/v1/prompts/${currentPromptId}/versions/${versionId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const version = data.data;
            
            // 填充版本内容
            document.getElementById('titleInput').value = version.title;
            document.getElementById('descriptionInput').value = version.description || '';
            editor.setValue(version.content);
            
            // 关闭历史面板
            document.getElementById('historyPanel').classList.remove('active');
            
            // 标记为有修改
            hasUnsavedChanges = true;
            updateSaveStatus('editing');
        }
    } catch (error) {
        console.error('加载版本失败:', error);
        alert('加载版本失败');
    }
}

/**
 * 切换专注模式
 */
function toggleFocusMode() {
    document.body.classList.toggle('focus-mode');
}

/**
 * 绑定事件
 */
function bindEvents() {
    // 返回按钮
    document.getElementById('backBtn').addEventListener('click', () => {
        if (hasUnsavedChanges) {
            if (confirm('有未保存的修改，确定要离开吗？')) {
                window.location.href = '/home';
            }
        } else {
            window.location.href = '/home';
        }
    });
    
    // 保存按钮
    document.getElementById('saveBtn').addEventListener('click', () => {
        savePrompt();
    });
    
    // 专注模式
    document.getElementById('focusBtn').addEventListener('click', toggleFocusMode);
    
    // 版本历史
    document.getElementById('historyBtn').addEventListener('click', showVersionHistory);
    
    // 测试按钮
    document.getElementById('testBtn').addEventListener('click', testPrompt);
    
    // 运行测试
    document.getElementById('runTestBtn').addEventListener('click', runTest);
    
    // 关闭测试面板
    document.getElementById('closePanelBtn').addEventListener('click', () => {
        document.getElementById('testPanel').classList.remove('active');
    });
    
    // 关闭历史面板
    document.getElementById('closeHistoryBtn').addEventListener('click', () => {
        document.getElementById('historyPanel').classList.remove('active');
    });
    
    // 添加标签
    document.getElementById('addTagBtn').addEventListener('click', () => {
        const selector = document.getElementById('tagSelector');
        selector.style.display = 'block';
        setTimeout(() => selector.classList.add('active'), 10);
    });
    
    // 关闭标签选择器
    document.getElementById('closeTagSelector').addEventListener('click', () => {
        const selector = document.getElementById('tagSelector');
        selector.classList.remove('active');
        setTimeout(() => selector.style.display = 'none', 300);
    });
    
    // Temperature滑块
    document.getElementById('temperatureSlider').addEventListener('input', (e) => {
        document.getElementById('temperatureValue').textContent = e.target.value;
    });
    
    // 复制结果
    document.getElementById('copyResultBtn').addEventListener('click', copyTestResult);
    
    // 监听页面离开事件
    window.addEventListener('beforeunload', (e) => {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '有未保存的修改，确定要离开吗？';
        }
    });
}

/**
 * 设置键盘快捷键
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Cmd/Ctrl + S: 保存
        if ((e.metaKey || e.ctrlKey) && e.key === 's') {
            e.preventDefault();
            savePrompt();
        }
        
        // Cmd/Ctrl + Enter: 测试
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            testPrompt();
        }
        
        // Cmd/Ctrl + /: 专注模式
        if ((e.metaKey || e.ctrlKey) && e.key === '/') {
            e.preventDefault();
            toggleFocusMode();
        }
        
        // Cmd/Ctrl + H: 历史版本
        if ((e.metaKey || e.ctrlKey) && e.key === 'h') {
            e.preventDefault();
            showVersionHistory();
        }
        
        // Esc: 退出专注模式或关闭面板
        if (e.key === 'Escape') {
            if (document.body.classList.contains('focus-mode')) {
                toggleFocusMode();
            } else if (document.getElementById('testPanel').classList.contains('active')) {
                document.getElementById('testPanel').classList.remove('active');
            } else if (document.getElementById('historyPanel').classList.contains('active')) {
                document.getElementById('historyPanel').classList.remove('active');
            } else if (document.getElementById('tagSelector').classList.contains('active')) {
                document.getElementById('tagSelector').classList.remove('active');
                setTimeout(() => document.getElementById('tagSelector').style.display = 'none', 300);
            }
        }
    });
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 7) {
        return date.toLocaleDateString('zh-CN');
    } else if (days > 0) {
        return `${days}天前`;
    } else if (hours > 0) {
        return `${hours}小时前`;
    } else if (minutes > 0) {
        return `${minutes}分钟前`;
    } else {
        return '刚刚';
    }
}