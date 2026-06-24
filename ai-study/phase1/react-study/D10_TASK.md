# D10：React 核心与项目骨架任务

## 今日必达

1. 理解 JSX、函数组件、props、state、事件、列表渲染。
2. 在 `src/App.tsx`、`src/components/TodoList.tsx`、`src/components/TodoForm.tsx` 中完成待办列表只读展示和新增表单雏形。
3. 所有组件 props 必须有明确 TypeScript 类型。

## 转岗强化

1. 把 D9 的 `Todo`、请求状态、状态迁移思路迁移到 React 页面心智里。
2. 能解释 React 与 Vue 在模板、响应式、数据流上的差异。
3. 能说明为什么不能直接修改数组 state。

## 滚动补强

1. 列表 key 选择策略。
2. 表单受控组件的完整机制。
3. 后续 D11 接 localStorage 与自定义 Hook。

## 手写范围

1. `TodoList`：根据 props 渲染列表；空列表时显示空状态。
2. `TodoForm`：接收输入值、变化事件和提交事件。
3. `App`：维护 todos 与输入框状态；完成新增 todo。

## 验收命令

```bash
npm run typecheck
npm run build
```

浏览器手测：

1. 页面能显示初始待办。
2. 输入标题并提交后，列表新增一条。
3. 空标题不应新增。
