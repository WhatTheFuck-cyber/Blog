# 博客前端

## 基于 Vite + Vue3 开发

### 1. 准备工作

**(1) 安装 [node.js](https://nodejs.org/zh-cn/download)，勾选 `npm + docker` 工具组合**

```bash
# 通过以下命令查看是否安装成功
node -v
npm -v
```

**(2) 创建 Vite + vue3 项目**

```bash
npm create vite@latest blog-fronthead-integration -- --template vue
```

**(3) 项目依赖安装**

```bash
npm install vue-router@4 pinia axios element-plus md-editor-v3 marked highlight.js vue3-draggable-resizable --save
```

**(4) 项目如果报警告可打补丁**
```bash
npm audit fix
```

**(5) 项目文件替换并启动**

```bash
npm run dev
```

### 2. 项目结构

```plaintext
├── public                      # 静态资源
├── src
│   ├── assets                  # 静态资源
│   ├── components              # 公共组件
│   ├── router                  # 路由管理
│   ├── store                   # 状态管理
│   ├── utils                   # 工具函数
│   ├── views                   # 页面组件
│   ├── App.vue
│   ├── main.js
|   └── style.css
├── .env.development            # 开发环境 url 配置
├── .env.production             # 生产环境 url 配置
├── .gitignore
├── index.html                  # 入口文件
├── package-lock.json           # 依赖版本锁定
├── package.json                # 项目依赖
├── README.md
└── vue.config.js                # vue 配置
```

### 3. 项目特点

- **模块化开发**：采用模块化开发方式，将项目分为多个模块，每个模块负责不同的功能，便于维护和扩展。
- **组件化开发**：采用组件化开发方式，将页面拆分为多个组件，每个组件负责不同的功能，便于复用和维护。

不过由于作者第一次开发 Vue3 项目，组件化和模块化不够彻底，如需接续开发，请重构项目代码结构。