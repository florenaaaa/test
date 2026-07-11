# 🤖 Agent 开发学习总结

> **技术栈**: LangGraph · LangChain · ChatOpenAI (通义千问) · ChromaDB  
> **学习模式**: 从基础 → 进阶 → 实战，逐步构建 Agent 系统

---

## 一、LangGraph 基础概念

### 核心组件
| 概念 | 说明 |
|------|------|
| **StateGraph** | 图的主体，定义状态流转结构 |
| **AgentState (TypedDict)** | 状态定义，节点间传递的数据结构 |
| **Node** | 图中的处理单元，接收状态 → 处理 → 返回新状态 |
| **Edge** | 节点间的连接，定义执行流程 |
| **START / END** | 图的入口和出口 |

### 图类型学习路径
1. **Hello** → 最简单的单节点图（greeting_node）
2. **SequentialGraph** → 多节点顺序执行（first → second → third）
3. **MultipleInputsGraph** → 多输入处理（列表聚合）
4. **ConditionalGraph** → 条件分支（根据 operation 选择 add/subtract）
5. **LoopingGraph** → 循环执行（counter 控制循环次数）

---

## 二、Agent 实现演进

### 📍 Agent_Boot.py — 最基础 Agent
```
START → [process: LLM调用] → END
```
- 单节点顺序图，无记忆
- 每次对话独立，不保留上下文
- 核心：`StateGraph` + `add_node` + `add_edge`

### 📍 Agent_Boot_Memory.py — 带记忆的 Agent
```
START → [process: LLM调用+追加历史] → END
```
**与 Boot 的区别：**
- 维护 `conversation_history` 列表
- 每次将历史消息一起传入 LLM
- 对话结束自动保存到 `logging.txt`
- **关键代码**: `state["messages"].append(AIMessage(...))`

### 📍 Agent_Boot_ReAct.py — ReAct 模式（工具调用）
```
START → [our_agent: LLM决策] → 条件判断
    → 需要工具 → [tools: 执行工具] → 回到 our_agent
    → 不需要 → END
```
**核心知识点：**
- `@tool` 装饰器定义工具（add/subtract/multiple）
- `model.bind_tools(tools)` 绑定工具到 LLM
- `add_conditional_edges` 实现条件路由
- `ToolNode` 自动执行工具调用
- `should_continue` 函数检查 `tool_calls` 决定是否循环
- `Annotated[Sequence[BaseMessage], add_messages]` 实现消息自动追加

### 📍 Agent_RAG.py — 检索增强生成（RAG）
```
PDF加载 → 文本分割 → ChromaDB向量化 → Retriever工具 → LLM回答
```
**完整 RAG 流水线：**
1. **文档加载**: `PyPDFLoader` 加载 PDF
2. **文本分割**: `RecursiveCharacterTextSplitter` (chunk_size=1000, overlap=200)
3. **向量嵌入**: `DashScopeEmbeddings` (text-embedding-v3)
4. **向量存储**: `Chroma` 持久化到本地 (`chroma.sqlite3`)
5. **检索器**: `similarity` 搜索，返回 top-k=5 个最相关块
6. **Retriever工具**: 将检索结果格式化为 LLM 可理解的上下文
7. **ReAct循环**: LLM 根据需要调用检索工具回答问题

### 📍 Agent_DRAFTER.py — 文档写作助手
```
START → [our_agent: 写作决策] → 条件判断
    → 需要工具 → [tools: update/save] → 回到 our_agent
    → 完成 → END
```
**自定义工具：**
- `update(content)`: 更新文档内容（全局变量存储）
- `save(filename)`: 保存文档到 .txt 文件
- System Prompt 中定义了助手角色和使用工具的规则

---

## 三、关键技术要点

### 1. 状态管理
| 方式 | 适用场景 |
|------|---------|
| `List[HumanMessage]` | 简单场景，手动管理 |
| `Annotated[Sequence[BaseMessage], add_messages]` | 自动追加，避免覆盖 |
| `List[Union[HumanMessage, AIMessage]]` | 混合消息类型 |

### 2. 条件边 (Conditional Edges)
```python
graph.add_conditional_edges(
    "node_name",
    router_function,    # 返回字符串标识
    {"continue": "next_node", "end": END}
)
```

### 3. 工具绑定
```python
@tool
def my_tool(param: str) -> str:
    """文档字符串很重要，LLM据此理解工具用途"""
    return result

model.bind_tools([my_tool])
```

### 4. RAG 关键参数
- **chunk_size**: 1000（块大小）
- **chunk_overlap**: 200（重叠，保持上下文连贯）
- **search_kwargs k**: 5（检索返回数量）

---

## 四、项目文件结构一览

```
├── Agent_Boot.py              # 最基础 Agent
├── Agent_Boot_Memory.py       # 带记忆 Agent
├── Agent_Boot_ReAct.py        # ReAct 工具调用
├── Agent_RAG.py              # RAG 检索增强
├── Agent_DRAFTER.py          # 文档写作助手
├── LangGraph-Hello.ipynb     # 基础图
├── LangGraph-SequentialGraph.ipynb  # 顺序图
├── LangGraph-ConditionalGraph.ipynb # 条件图
├── LangGraph-LoopingGraph.ipynb     # 循环图
├── LangGraph-MultipleInputsGraph.ipynb  # 多输入图
├── agent_create_1/2/3.py     # Agent 创建系列
├── chroma.sqlite3            # 向量数据库
├── logging.txt               # 对话日志
└── skills/                   # 17个 skill 模块
```

---

## 五、学习收获

### ✅ 已掌握
- [x] LangGraph 图的构建与编译
- [x] 状态定义与传递（TypedDict）
- [x] 节点、边、条件边的使用
- [x] ReAct 模式（思考-行动-观察循环）
- [x] 工具定义与绑定（@tool）
- [x] RAG 完整流程（加载→分割→嵌入→存储→检索→生成）
- [x] ChromaDB 向量数据库使用
- [x] 对话记忆与持久化

### 🔜 下一步学习方向
1. **Human-in-the-Loop**: 人工审批、中断与恢复
2. **Subgraphs**: 子图嵌套与模块化
3. **Persistence/Checkpointing**: 状态持久化与时间旅行
4. **Streaming**: 流式输出
5. **Multi-Agent**: 多 Agent 协作（Supervisor、Hierarchical）
6. **高级 RAG**: 多查询、HyDE、重排序
7. **Agent 评估**: 测试与评测框架

---

> 📅 生成时间: 2026-04-05  
> 🛠️ 生成方式: doc-coauthoring skill 辅助分析
