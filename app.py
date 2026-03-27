import streamlit as st
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from tools import tools

load_dotenv()

# ---------- 1. 配置模型（直接使用 ChatOpenAI，避免 provider 参数） ----------
llm = ChatOpenAI(
    model="deepseek-ai/DeepSeek-V3.2",
    openai_api_key=os.getenv("siliconFlow_API_KEY"),
    openai_api_base="https://api.siliconflow.cn/v1",
    temperature=0.3,
    max_tokens=8192,
    timeout=60
)

# ---------- 2. 记忆 ----------
checkpointer = InMemorySaver()

# ---------- 3. 系统提示词 ----------
SYSTEM_PROMPT = """你是一个乐于助人的助手，可以调用以下工具来回答问题：
- add_tool: 计算两个数字的和
- multiply_tool: 计算两个数字的乘积
- weather_tool: 查询指定城市的实时天气
- rag_search_tool: 在图书馆知识库中检索信息（借阅规则、开放时间等）

请根据用户问题选择合适的工具，并提供准确、友好的回答。"""

# ---------- 4. 创建 Agent ----------
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer
)

# ---------- 5. Streamlit UI ----------
st.set_page_config(page_title="AI 智能助手", page_icon="🤖")
st.title("🤖 你的智能助手")
st.markdown("我可以帮你查图书馆信息、查天气、做数学计算，还能记住对话内容！")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user_001"

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("请输入你的问题："):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            try:
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config=config
                )
                last_message = result["messages"][-1]
                answer = last_message.content
                st.markdown(answer)
            except Exception as e:
                st.error(f"出错了：{e}")
                answer = "抱歉，我遇到了一些问题，请稍后再试。"

    st.session_state.messages.append({"role": "assistant", "content": answer})

with st.sidebar:
    if st.button("清除对话历史"):
        st.session_state.messages = []
        st.session_state.thread_id = f"user_{hash(str(st.session_state))}"
        st.rerun()