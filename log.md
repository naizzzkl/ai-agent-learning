# 学习日志 - Day2 (2026-03-19)

## 完成内容
- 学习了提示词工程，练习让AI输出JSON格式。
- 测试了temperature参数对输出的影响。
- 成功调用API并处理了Markdown代码块问题。

## 遇到的问题
- AI返回的内容被包裹在```json ...```中，导致json.loads()解析失败。
- 解决方案：用正则提取JSON部分，或改进提示词要求“只输出纯净JSON”。

## 收获
- 掌握了让AI输出结构化数据的方法，为后续RAG和Agent打下基础。
- 学会了用try-except处理JSON解析异常。

# 学习日志 - Day3 (2026-03-19)

## 完成内容
- [x] 少样本提示练习：让AI模仿格式生成菜谱。
- [x] 思维链练习：让AI分步解数学题。
- [x] 收集了3份校园文档：notice.txt, menu.txt, library.txt。
- [x] 安装LangChain，用TextLoader加载txt文档。
- [x] 用RecursiveCharacterTextSplitter切分文档，探索不同参数效果。

## 遇到的问题
- 一开始在jupyter下载langchain库，显示成功下载但是无法调用
- 对于recursivecharactertextsplitter的不理解

## 解决过程
- 查询ai，将下载地址放在了我的虚拟环境中，保证了env_name可以调用
- 无法下载，下载了greenlet库，再次下载成功解决问题
- 多次尝试，对语句进行各种改动，已经完全掌握

## 今日收获
- 少样本提示能有效控制输出格式，思维链让推理更透明。
- chunk_size和chunk_overlap需要根据文档内容调整，过小会割裂语义，过大会降低检索精度。

## 明日计划
- 学习Embedding和向量数据库，为RAG搭建完整流程。

# 学习日志 - Day4 (2026-03-20)

## 完成内容
- [x] 用requests库直接调用DeepSeek API，理解HTTP请求
- [x] 封装`deepseek_chat`函数，支持参数和异常处理
- [x] 学习Embedding概念，用LangChain生成向量并存入Chroma
- [x] 实现相似性检索，并搭建完整RAG问答流程
- [x] 测试了不同chunk_size和k值的效果

## 参数实验记录
- chunk_size=200, chunk_overlap=20 → 块数：XX
- 检索k=3时，返回的块内容：...（记录一个例子）
- 修改k=5，回答质量变化：...

## 遇到的问题
- 找不到方闻馆块
## 今日收获
- 理解了RAG的两阶段：检索 + 生成。
- 封装函数让代码更简洁，便于复用。

## 明日计划
- 学习Agent基础：Tool调用、ReAct框架
- 用LangChain实现一个简单Agent
# 学习日志 - Day4 (2026-03-20)

## 完成内容
- [x] 加载 `library.txt` 文档，使用 `RecursiveCharacterTextSplitter` 切分（chunk_size=500, overlap=50），生成5个块。
- [x] 使用硅基流动嵌入模型 `BAAI/bge-large-zh-v1.5` 构建 Chroma 向量数据库，持久化到 `./chroma_db`。
- [x] 实现基础 RAG 问答函数，将检索到的文档块作为上下文，调用大模型生成答案。
- [x] 测试检索：用“方闻馆详细时间”查询，发现检索结果固定为“借阅权限”块，未能命中目标块。
- [x] 通过打印所有块，确认“方闻馆详细时间”存在于第1块。
- [x] 分析原因：`Chroma.from_documents` 在 `persist_directory` 已存在时直接加载旧库，修改切分参数后未重建。
- [x] 手动删除 `chroma_db` 文件夹，重新运行代码，重建数据库。
- [x] 重建后检索“方闻馆开放时间”，成功命中第1块（详细时间内容）。

## 遇到的问题
1. **检索结果固定**：无论查询什么内容，`similarity_search` 都返回相同的借阅权限块。
2. **原因**：切分参数改变后，向量数据库未更新，仍使用旧数据。
3. **解决**：删除 `chroma_db` 目录，强制重建数据库，新参数生效。

## 解决过程
- 通过 `for i, chunk in enumerate(chunks): if "方闻馆" in chunk.page_content: print(...)` 确认目标块存在。
- 意识到 `Chroma.from_documents` 在目录存在时不会重新构建，于是手动删除目录。
- 重建后，用 `similarity_search` 测试“方闻馆 开放时间”，返回块中包含详细时间，问题解决。

## 今日收获
- 理解了向量数据库的持久化机制：`persist_directory` 存在时直接加载，不会自动更新。
- 掌握了调试 RAG 检索的方法：打印所有块内容、检查目标块是否存在、确认数据库是否最新。
- 成功搭建了完整的 RAG 流程（加载→切分→向量化→检索→生成），能够回答基于文档的问题。

## 关键代码片段
```python
# 切分参数
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)

# 构建向量库（首次运行会生成，后续直接加载）
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 检索与生成
def rag_answer(question, vectorstore, k=2):
    docs = vectorstore.similarity_search(question, k=k)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"参考资料：{context}\n\n问题：{question}\n回答："
    response = llm.invoke(prompt)
    return response.content

# 学习日志 - Day5 (2026-03-21)

## 完成内容
- [x] 实现条件重建数据库（REBUILD 标志 + 指纹法）
- [x] 使用 MMR 检索，对比与相似性检索的差异
- [x] 实现 BM25 + 向量混合检索，调整权重观察效果
- [x] 尝试检索后压缩，理解其优缺点
- [x] 预处理文档（表格转自然语言），测试检索提升

## 效果对比表
| 方法 | 是否命中目标块 | 块数量 | 答案质量 |
|------|---------------|--------|----------|
| 相似性检索 | 否 | 2 | 差 |
| MMR | 是 | 3 | 中 |
| 混合检索 | 是 | 3 | 良 |
| 压缩检索 | 是 | 2 | 优 |
| 预处理+混合 | 是 | 3 | 优 |

## 关键代码
（粘贴你实现的关键函数）

## 遇到的问题
- （记录）

## 明日计划
- 将优化后的 RAG 封装为可重用模块
- 学习 Agent 基础（Tool 调用、ReAct 框架）



    # 学习日志 - Day6 (2026-03-24)

## 完成内容
- [x] 理解 ReAct 框架（Thought → Action → Observation → Thought 循环）
- [x] 使用 `@tool` 装饰器定义自定义工具（加法、乘法）
- [x] 使用 `create_react_agent` 和 `AgentExecutor` 创建并执行 Agent
- [x] 测试 Agent 对简单数学问题的响应，观察 verbose 输出
- [x] 尝试自定义提示词模板（中文版），遇到 `{chat_history}` 变量缺失错误
- [x] 学习两种解决方案：① 移除 `{chat_history}`（单轮对话）② 正确配置 memory（多轮对话）

## 遇到的问题
1. **提示词模板变量错误**  
   在尝试将模板改为中文并加入 `{chat_history}` 后，运行报错：  
   `KeyError: Input to ChatPromptTemplate is missing variables {'chat_history'}.`  
   原因是 `create_react_agent` 默认只传递 `input`、`intermediate_steps`、`tools`、`tool_names`，不包含 `chat_history`。

## 解决过程
- 查阅 LangChain 文档，确认 `AgentExecutor` 支持通过 `memory` 参数注入 `chat_history`，但需要在模板中声明 `{chat_history}`，并在创建 AgentExecutor 时传入 `memory` 对象。
- 由于今天的学习重点是掌握 Agent 基础工具调用，暂时不需要多轮对话，因此选择**方案一**：从模板中移除 `{chat_history}` 占位符，保持模板简洁，避免报错。
- 如需后续添加记忆，可按照官方文档配置 `ConversationBufferMemory` 和自定义提示词。

## 今日收获
- 理解了 ReAct 提示词模板的结构：`{tools}`、`{tool_names}`、`{input}`、`{agent_scratchpad}` 的作用。
- 学会了用 `@tool` 装饰器快速定义工具，并通过 `docstring` 自动生成工具描述，供 LLM 理解。
- 掌握了 `create_react_agent` 和 `AgentExecutor` 的使用，通过 `verbose=True` 看到 Agent 的思考链。
- 体验了 LLM 根据提示词自主选择工具、解析输入、观察结果并最终回答的过程。

## 关键代码片段
```python
# 定义工具
@tool
def add_tool(input_str: str) -> str:
    """计算两个数字的和。输入格式：数字1,数字2 或 数字1 数字2"""
    parts = input_str.replace(',', ' ').split()
    a, b = map(float, parts[:2])
    return f"{a} + {b} = {a + b}"

# 创建 Agent
agent = create_react_agent(llm, tools, react_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 测试
result = agent_executor.invoke({"input": "3 + 5 等于多少？"})
print(result["output"])



# 学习日志 - Day7 (2026-03-24)

## 完成内容
- [x] 理解对话记忆在 Agent 中的作用
- [x] 使用 `ConversationBufferMemory` 保存完整历史
- [x] 自定义包含 `{chat_history}` 的提示词模板
- [x] 将记忆集成到 `AgentExecutor`，测试多轮对话
- [x] 探索其他记忆类型：`ConversationBufferWindowMemory`、`ConversationSummaryMemory`
- [x] 完成小练习：
    - 修改记忆窗口大小为 1，验证只能记住最近一轮
    - 将提示词模板改为中文，测试记忆效果
    - 模拟多轮对话（5轮），检查 Agent 能否回忆早期信息

## 遇到的问题
1. **中文模板中 `{chat_history}` 占位符的格式问题**  
   第一次使用中文模板时，直接复制了英文格式，但 `ChatPromptTemplate` 要求 `{chat_history}` 必须正确传递。由于忘记在 `memory_key` 中保持一致，导致历史未注入。  
2. **`ConversationBufferWindowMemory` 设置 `k=1` 后，第二轮对话无法回忆第一轮的内容**  
   符合预期，但验证了窗口机制有效。  
3. **`ConversationSummaryMemory` 在长对话中消耗 token 较多，且摘要有时会丢失细节**  
   需要权衡成本和精度，在简单场景下 `BufferMemory` 更直接。

## 解决过程
- 检查模板中变量名与 `memory_key` 是否完全一致（均为 `chat_history`）。  
- 确认 `return_messages=True` 以保证与 `ChatPromptTemplate` 兼容。  
- 使用 `print(memory.chat_memory.messages)` 查看历史内容，验证记忆是否存储。  
- 对于 `ConversationSummaryMemory`，尝试调整 `summary_prompt` 以改善摘要质量，但保留了默认。

## 今日收获
- 掌握了 LangChain 记忆模块的核心概念和集成方法。  
- 理解了不同记忆类型的适用场景：
  - `ConversationBufferMemory`：简单直接，适合短对话。
  - `ConversationBufferWindowMemory`：节省 token，适合实时交互。
  - `ConversationSummaryMemory`：适合长对话，但会丢失部分细节且消耗额外 token。  
- 体验了带记忆的 Agent 在多轮对话中如何利用历史信息，显著提升交互体验。  
- 中文提示词同样有效，但需注意变量名和模板结构的准确性。

## 关键代码片段
```python
# 带记忆的提示词模板
react_prompt = ChatPromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Previous conversation:
{chat_history}

Use the following format:
...
Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

# 创建记忆
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 创建 Agent 和 Executor
agent = create_react_agent(llm, tools, react_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)

# 测试多轮
agent_executor.invoke({"input": "我叫小明"})
agent_executor.invoke({"input": "我叫什么名字？"})  # 能记住

