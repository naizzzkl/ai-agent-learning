import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ==================== 嵌入模型配置 ====================
def get_embeddings():
    return OpenAIEmbeddings(
        model="BAAI/bge-large-zh-v1.5",
        openai_api_key=os.getenv("siliconFlow_API_KEY"),
        openai_api_base="https://api.siliconflow.cn/v1"
    )

# ==================== 加载向量库 ====================
_current_dir = os.path.dirname(__file__)
_persist_dir = os.path.join(_current_dir, "chroma_db")
_embeddings = get_embeddings()

try:
    vectorstore = Chroma(
        persist_directory=_persist_dir,
        embedding_function=_embeddings
    )
    print("向量库加载成功")
except Exception as e:
    print(f"向量库加载失败: {e}")
    vectorstore = None

def _search_library(query: str, k: int = 3) -> str:
    if vectorstore is None:
        return "向量库未加载，无法检索。"
    docs = vectorstore.max_marginal_relevance_search(query, k=k, fetch_k=k*3)
    if not docs:
        return "未找到相关信息。"
    return "\n\n".join([doc.page_content for doc in docs])

# ==================== 工具1：加法 ====================
@tool
def add_tool(a: float, b: float) -> str:
    """计算两个数字的和。"""
    result = a + b
    return f"{a} + {b} = {result}"

# ==================== 工具2：乘法 ====================
@tool
def multiply_tool(a: float, b: float) -> str:
    """计算两个数字的乘积。"""
    result = a * b
    return f"{a} × {b} = {result}"

# ==================== 工具3：天气查询 ====================
def _get_weather(city: str) -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "错误：未配置天气 API 密钥。"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=zh_cn"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if resp.status_code != 200:
            return f"查询失败：{data.get('message', '未知错误')}"
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        hum = data["main"]["humidity"]
        return f"{city} 天气：{desc}，温度 {temp}℃，湿度 {hum}%"
    except Exception as e:
        return f"天气查询出错：{e}"

@tool
def weather_tool(city: str) -> str:
    """查询指定城市的实时天气。"""
    return _get_weather(city)

# ==================== 工具4：RAG 检索 ====================
@tool
def rag_search_tool(query: str) -> str:
    """在图书馆知识库中检索信息。当用户询问图书馆相关规则、开放时间、借阅等问题时使用。"""
    return _search_library(query, k=3)

# ==================== 导出工具列表 ====================
tools = [add_tool, multiply_tool, weather_tool, rag_search_tool]