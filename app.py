import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from tools import tools  # 假设你的工具都在 tools.py 中定义
import logging
import os
from datetime import datetime

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
# 加载环境变量（.env 文件中的 API Key）
load_dotenv()

# ---------- 1. 配置 LLM ----------
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V3",
    openai_api_key=os.getenv("siliconFlow_API_KEY"),
    openai_api_base="https://api.siliconflow.cn/v1",
    temperature=0.3
)

# ---------- 2. 提示词模板（包含历史记忆） ----------
react_prompt = ChatPromptTemplate.from_template("""
Answer the following questions as best you can. You have access to the following tools:

{tools}

Previous conversation:
{chat_history}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

# ---------- 3. 记忆（使用 Streamlit 的 session_state 保存） ----------
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

# ---------- 4. 创建 Agent ----------
agent = create_react_agent(llm, tools, react_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=st.session_state.memory,
    verbose=False,          # 生产环境关闭 verbose，可减少日志
    max_iterations=5,
    handle_parsing_errors=True
)

# ---------- 5. Streamlit 界面 ----------
st.set_page_config(page_title="AI 智能助手", page_icon="🤖")
st.title("🤖 你的智能助手")
st.markdown("我可以帮你查图书馆信息、查天气、做数学计算，还能记住对话内容！")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 接收用户输入
if prompt := st.chat_input("请输入你的问题："):
    # 添加用户消息到界面
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

# 在调用 agent_executor 前后添加日志
    logger.info(f"用户提问：{prompt}")
    response = agent_executor.invoke({"input": prompt})
    answer = response["output"]
    logger.info(f"Agent 回答：{answer[:200]}...")  # 只记录前200字符避免日志过长

    # 调用 Agent
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = agent_executor.invoke({"input": prompt})
                answer = response["output"]
                st.markdown(answer)
            except Exception as e:
                st.error(f"出错了：{e}")
                answer = "抱歉，我遇到了一些问题，请稍后再试。"
    # 在调用 agent_executor 前后添加日志
    logger.info(f"用户提问：{prompt}")
    response = agent_executor.invoke({"input": prompt})
    answer = response["output"]
    logger.info(f"Agent 回答：{answer[:200]}...")  # 只记录前200字符避免日志过长
    # 保存助手回复
    st.session_state.messages.append({"role": "assistant", "content": answer})

