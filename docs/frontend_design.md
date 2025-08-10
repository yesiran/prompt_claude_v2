# 前端界面设计方案

## 设计理念
- **极简主义**：去除一切不必要的元素
- **沉浸体验**：让用户专注于内容创作
- **流畅交互**：每个操作都有即时反馈
- **视觉呼吸**：大量留白，元素间距适中

## 技术架构

### 核心技术栈
- **框架**：原生JavaScript + 少量jQuery（保持轻量）
- **样式**：CSS3 + CSS Variables（主题切换）
- **编辑器**：CodeMirror（Markdown编辑器）
- **动画**：CSS Transitions + RequestAnimationFrame
- **状态管理**：简单的发布订阅模式

## 页面结构设计

### 1. 整体布局
```
┌─────────────────────────────────────────────┐
│                  顶部导航栏                   │
├────────┬────────────────────────────────────┤
│        │                                    │
│  侧边栏  │            主内容区                │
│        │                                    │
│        │                                    │
└────────┴────────────────────────────────────┘
```

### 2. 页面组件定义

#### 2.1 登录页面 (login.html)
```html
<!-- 极简登录界面 -->
<div class="auth-container">
    <div class="auth-card">
        <h1 class="auth-title">静思</h1>
        <p class="auth-subtitle">让思维沉淀的地方</p>
        
        <form class="auth-form">
            <input type="email" placeholder="邮箱" class="auth-input">
            <input type="password" placeholder="密码" class="auth-input">
            <button type="submit" class="auth-button">进入</button>
        </form>
        
        <p class="auth-switch">
            还没有账号？<a href="#">创建</a>
        </p>
    </div>
    
    <!-- 背景装饰 -->
    <div class="auth-background"></div>
</div>
```

#### 2.2 主界面 (index.html)
```html
<!-- 主界面结构 -->
<div class="app-container">
    <!-- 顶部导航 -->
    <header class="app-header">
        <div class="header-left">
            <button class="menu-toggle">☰</button>
            <span class="app-logo">静思</span>
        </div>
        
        <div class="header-center">
            <input type="search" class="search-bar" placeholder="搜索...">
        </div>
        
        <div class="header-right">
            <button class="setting-btn">⚙</button>
            <div class="user-avatar"></div>
        </div>
    </header>
    
    <!-- 侧边栏 -->
    <aside class="app-sidebar">
        <nav class="sidebar-nav">
            <a href="#" class="nav-item active">
                <span class="nav-icon">📝</span>
                <span class="nav-text">我的Prompt</span>
            </a>
            <a href="#" class="nav-item">
                <span class="nav-icon">👥</span>
                <span class="nav-text">协作空间</span>
            </a>
            <a href="#" class="nav-item">
                <span class="nav-icon">🏷️</span>
                <span class="nav-text">标签管理</span>
            </a>
            <a href="#" class="nav-item">
                <span class="nav-icon">📊</span>
                <span class="nav-text">测试历史</span>
            </a>
        </nav>
        
        <!-- 标签过滤 -->
        <div class="tag-filter">
            <h3 class="filter-title">标签筛选</h3>
            <div class="tag-list">
                <span class="tag-item active">全部</span>
                <span class="tag-item">工作</span>
                <span class="tag-item">学习</span>
                <span class="tag-item">创作</span>
            </div>
        </div>
    </aside>
    
    <!-- 主内容区 -->
    <main class="app-main">
        <div class="prompt-grid">
            <!-- Prompt卡片 -->
            <div class="prompt-card">
                <div class="card-header">
                    <h3 class="card-title">Prompt标题</h3>
                    <span class="card-version">v1.2</span>
                </div>
                <p class="card-preview">这是Prompt的预览内容...</p>
                <div class="card-tags">
                    <span class="tag">工作</span>
                    <span class="tag">GPT-5</span>
                </div>
                <div class="card-footer">
                    <span class="card-date">2天前</span>
                    <span class="card-stats">
                        <span>👁 12</span>
                        <span>🧪 5</span>
                    </span>
                </div>
            </div>
            
            <!-- 新建卡片 -->
            <div class="prompt-card new-card">
                <div class="new-card-content">
                    <span class="new-icon">+</span>
                    <span class="new-text">创建新Prompt</span>
                </div>
            </div>
        </div>
    </main>
</div>

<!-- 背景音乐控制 -->
<div class="music-control">
    <button class="music-toggle">🎵</button>
    <select class="music-select">
        <option>雨声</option>
        <option>森林</option>
        <option>轻钢琴</option>
    </select>
</div>
```

#### 2.3 编辑页面 (editor.html)
```html
<!-- 编辑器界面 -->
<div class="editor-container">
    <!-- 编辑器头部 -->
    <header class="editor-header">
        <div class="header-left">
            <button class="back-btn">←</button>
            <input type="text" class="title-input" placeholder="无标题Prompt">
        </div>
        
        <div class="header-center">
            <span class="save-status">已保存</span>
            <span class="version-info">版本 1.2</span>
        </div>
        
        <div class="header-right">
            <button class="save-btn" title="保存 (Cmd+S)">
                <svg width="16" height="16" viewBox="0 0 24 24">
                    <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/>
                    <polyline points="17 21 17 13 7 13 7 21"/>
                    <polyline points="7 3 7 8 15 8"/>
                </svg>
                保存
            </button>
            <button class="test-btn">测试运行</button>
            <button class="history-btn">历史版本</button>
            <button class="share-btn">协作</button>
        </div>
    </header>
    
    <!-- 编辑器主体 -->
    <div class="editor-body">
        <!-- 标签栏 -->
        <div class="tag-bar">
            <div class="selected-tags">
                <span class="tag removable">工作 ×</span>
                <span class="tag removable">GPT-5 ×</span>
            </div>
            <button class="add-tag-btn">+ 添加标签</button>
        </div>
        
        <!-- 编辑区域 -->
        <div class="editor-wrapper">
            <textarea id="prompt-editor" class="editor-textarea"></textarea>
        </div>
        
        <!-- 描述区域 -->
        <div class="description-area">
            <input type="text" class="description-input" 
                   placeholder="添加描述（可选）">
        </div>
    </div>
    
    <!-- 焦点模式遮罩 -->
    <div class="focus-overlay"></div>
</div>

<!-- 测试面板 -->
<div class="test-panel">
    <div class="panel-header">
        <h3>测试Prompt</h3>
        <button class="panel-close">×</button>
    </div>
    
    <div class="panel-body">
        <div class="model-select">
            <label>
                <input type="radio" name="model" value="gpt-5" checked>
                GPT-5
            </label>
            <label>
                <input type="radio" name="model" value="claude">
                Claude Opus 4.1
            </label>
        </div>
        
        <div class="test-input">
            <textarea placeholder="输入测试内容（可选）"></textarea>
        </div>
        
        <button class="run-test-btn">运行测试</button>
        
        <div class="test-result">
            <div class="result-header">
                <span class="result-model">GPT-5</span>
                <span class="result-time">1.2s</span>
            </div>
            <div class="result-content"></div>
        </div>
    </div>
</div>
```

## 样式设计

### 1. 设计令牌（Design Tokens）
```css
:root {
    /* 颜色系统 */
    --color-primary: #4A5568;      /* 主色：优雅灰 */
    --color-secondary: #718096;    /* 次要色 */
    --color-accent: #5B8DEE;       /* 强调色：静谧蓝 */
    --color-background: #FFFFFF;   /* 背景色 */
    --color-surface: #F7FAFC;      /* 表面色 */
    --color-border: #E2E8F0;       /* 边框色 */
    --color-text: #2D3748;         /* 文本色 */
    --color-text-light: #A0AEC0;   /* 浅文本色 */
    
    /* 间距系统 */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;
    
    /* 字体系统 */
    --font-serif: 'Crimson Text', 'Songti SC', serif;
    --font-sans: 'Inter', 'PingFang SC', sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', monospace;
    
    /* 字号系统 */
    --text-xs: 12px;
    --text-sm: 14px;
    --text-base: 16px;
    --text-lg: 18px;
    --text-xl: 24px;
    --text-2xl: 32px;
    
    /* 圆角系统 */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-full: 9999px;
    
    /* 阴影系统 */
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
    --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
    
    /* 动画时长 */
    --duration-fast: 150ms;
    --duration-normal: 300ms;
    --duration-slow: 500ms;
}
```

### 2. 核心组件样式

#### 2.1 卡片样式
```css
.prompt-card {
    background: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    transition: all var(--duration-normal) ease;
    cursor: pointer;
}

.prompt-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--color-accent);
}

.prompt-card.new-card {
    border: 2px dashed var(--color-border);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
    background: var(--color-surface);
}
```

#### 2.2 编辑器样式
```css
.editor-textarea {
    width: 100%;
    min-height: 500px;
    padding: var(--spacing-xl);
    border: none;
    font-family: var(--font-mono);
    font-size: var(--text-base);
    line-height: 1.8;
    color: var(--color-text);
    background: transparent;
    resize: none;
}

.editor-textarea:focus {
    outline: none;
}

/* 焦点模式 */
.focus-mode .editor-header,
.focus-mode .tag-bar,
.focus-mode .description-area {
    opacity: 0.2;
    transition: opacity var(--duration-slow) ease;
}

.focus-mode .editor-header:hover,
.focus-mode .tag-bar:hover,
.focus-mode .description-area:hover {
    opacity: 1;
}
```

#### 2.3 标签样式
```css
.tag {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-sm);
    background: var(--color-surface);
    color: var(--color-text);
    border-radius: var(--radius-full);
    font-size: var(--text-sm);
    border: 1px solid var(--color-border);
    transition: all var(--duration-fast) ease;
}

.tag:hover {
    background: var(--color-accent);
    color: white;
    border-color: var(--color-accent);
}

.tag.removable {
    padding-right: var(--spacing-md);
    position: relative;
}
```

## 交互设计

### 1. 动画效果
```javascript
// 页面过渡动画
const pageTransition = {
    enter: 'fadeIn 300ms ease-out',
    leave: 'fadeOut 200ms ease-in'
};

// 元素出现动画
const elementAnimation = {
    card: 'slideUp 400ms ease-out',
    modal: 'zoomIn 300ms ease-out'
};
```

### 2. 快捷键
```javascript
const shortcuts = {
    'Cmd+S': '保存',
    'Cmd+Enter': '测试运行',
    'Cmd+K': '快速搜索',
    'Cmd+/': '切换焦点模式',
    'Cmd+H': '查看历史版本',
    'Esc': '退出当前模式'
};
```

### 3. 自动保存
```javascript
// 防抖自动保存
let saveTimer;
function autoSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
        // 执行保存
        savePrompt();
        showSaveStatus('已保存');
    }, 3000);
}
```

## 响应式设计

### 断点定义
```css
/* 移动端优先 */
@media (min-width: 640px) { /* 平板 */ }
@media (min-width: 1024px) { /* 桌面 */ }
@media (min-width: 1280px) { /* 大屏 */ }
```

### 自适应布局
- 移动端：单列布局，隐藏侧边栏
- 平板：双列布局，可收起侧边栏
- 桌面：三列布局，完整显示

## 主题系统

### 1. 亮色主题（默认）
```css
[data-theme="light"] {
    --color-background: #FFFFFF;
    --color-text: #2D3748;
}
```

### 2. 暗色主题
```css
[data-theme="dark"] {
    --color-background: #1A202C;
    --color-text: #E2E8F0;
}
```

### 3. 护眼主题
```css
[data-theme="sepia"] {
    --color-background: #F7F3ED;
    --color-text: #3E3E3E;
}
```

## 性能优化

1. **懒加载**：图片和非关键资源延迟加载
2. **虚拟滚动**：长列表只渲染可见区域
3. **防抖节流**：优化频繁触发的事件
4. **CSS动画**：优先使用transform和opacity
5. **缓存策略**：本地存储常用数据

## 无障碍设计

1. **键盘导航**：所有功能可通过键盘访问
2. **屏幕阅读**：适当的ARIA标签
3. **对比度**：确保文本可读性
4. **焦点提示**：清晰的焦点状态