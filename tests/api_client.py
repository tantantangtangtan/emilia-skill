"""
AI API 客户端

支持任何 OpenAI 兼容接口OpenAI、Azure、Ollama、vLLM 等）。
通过 .env 文件配置，适配不同测试环境。
"""

import os
from openai import OpenAI
from dotenv import load_dotenv


class ApiClient:
    """AI API 客户端，封装对话生成"""

    def __init__(self, system_prompt: str = ""):
        # 加载 .env 配置
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        load_dotenv(env_path)

        self.base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
        self.api_key = os.getenv("API_KEY", "")
        self.model = os.getenv("API_MODEL", "gpt-4o")
        self.temperature = float(os.getenv("API_TEMPERATURE", "0.5"))
        self.system_prompt = system_prompt

        if not self.api_key:
            raise ValueError(
                "未配置 API_KEY。\n"
                "请复制 .env.example 为 .env 并填入你的 API 配置。\n"
                "或设置环境变量 API_KEY、API_BASE_URL、API_MODEL。"
            )

        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def chat(self, messages: list[dict], temperature: float = None) -> str:
        """
        发送对话并获取回复

        参数:
            messages: 消息列表 [{"role": "user"/"assistant", "content": "..."}]
            temperature: 生成温度，默认使用 .env 中的 API_TEMPERATURE

        返回:
            AI 回复文本
        """
        if temperature is None:
            temperature = self.temperature

        full_messages = [{"role": "system", "content": self.system_prompt}]
        full_messages.extend(messages)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[API 错误] {e}"
