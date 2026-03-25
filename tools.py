# tools.py
import logging

# 创建一个以模块命名的记录器
logger = logging.getLogger(__name__)


import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 加载环境变量（必须在模块加载时执行）
load_dotenv()


# ==================== 嵌入模型配置 ====================
def get_embeddings():
    """返回与创建向量库时相同的嵌入模型对象"""
    return OpenAIEmbeddings(
        model="BAAI/bge-large-zh-v1.5",
        openai_api_key=os.getenv("siliconFlow_API_KEY"),
        openai_api_base="https://api.siliconflow.cn/v1"
    )


# ==================== 加载向量库（模块级别，只加载一次）====================
# 使用绝对路径或相对路径（相对于当前文件位置）
_current_dir = os.path.dirname(__file__)
_persist_dir = os.path.join(_current_dir, "chroma_db")
_embeddings = get_embeddings()

# 尝试加载向量库
try:
    vectorstore = Chroma(
        persist_directory=_persist_dir,
        embedding_function=_embeddings
    )
    print("向量库加载成功")
except Exception as e:
    print(f"向量库加载失败: {e}")
    vectorstore = None


# ==================== 工具1：加法 ====================
@tool
def add_tool(input_str: str) -> str:
    """
    计算两个数字的和。

    输入格式：数字1,数字2 或 数字1 数字2
    """
    try:
        parts = input_str.replace(',', ' ').split()
        if len(parts) != 2:
            return "错误：需要两个数字，用空格或逗号分隔。"
        a = float(parts[0])
        b = float(parts[1])
        result = a + b
        return f"{a} + {b} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


# ==================== 工具2：乘法 ====================
@tool
def multiply_tool(input_str: str) -> str:
    """
    计算两个数字的乘积。

    输入格式：数字1,数字2 或 数字1 数字2
    """
    try:
        parts = input_str.replace(',', ' ').split()
        if len(parts) != 2:
            return "错误：需要两个数字，用空格或逗号分隔。"
        a = float(parts[0])
        b = float(parts[1])
        result = a * b
        return f"{a} × {b} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


# ==================== 工具3：天气查询 ====================
def _get_weather(city: str) -> str:
    """实际调用 OpenWeatherMap API"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "错误：未配置天气 API 密钥，请在 .env 文件中添加 OPENWEATHER_API_KEY。"
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
    """查询指定城市的实时天气。输入城市名（例如：北京）。"""
    logger.info(f"weather_tool 被调用，城市：{city}")
    try:
        result = _get_weather(city)
        logger.info(f"weather_tool 返回：{result[:50]}...")
        return result
    except Exception as e:
        logger.error(f"weather_tool 异常: {e}", exc_info=True)
        return "天气查询失败。"


# ==================== 工具4：RAG 检索 ====================
def _search_library(query: str, k: int = 3) -> str:
    """在图书馆知识库中检索"""
    if vectorstore is None:
        return "向量库未加载，无法检索。"
    docs = vectorstore.similarity_search(query, k=k)
    if not docs:
        return "未找到相关信息。"
    return "\n\n".join([doc.page_content for doc in docs])


@tool
def rag_search_tool(query: str) -> str:
    """在图书馆知识库中检索信息。当用户询问图书馆相关规则、开放时间、借阅等问题时使用。"""
    logger.info(f"rag_search_tool 被调用，查询：{query}")
    try:
        result = _search_library(query, k=3)
        logger.info(f"rag_search_tool 返回结果长度：{len(result)} 字符")
        return result
    except Exception as e:
        logger.error(f"rag_search_tool 异常: {e}", exc_info=True)
        return "检索失败，请稍后重试。"


# ==================== 导出工具列表 ====================
tools = [add_tool, multiply_tool, weather_tool, rag_search_tool]