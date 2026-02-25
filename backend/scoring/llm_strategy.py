from .strategies import ScoringStrategy
from typing import Dict, Any
import re
import os
import requests
import logging

logger = logging.getLogger(__name__)


class LLMScoringStrategy(ScoringStrategy):
    """
    基于大语言模型的评分策略
    使用 DeepSeek API 进行智能评分
    """

    def __init__(self, api_key=None, api_url=None, model='deepseek-chat'):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.api_url = api_url or os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/chat/completions')
        self.model = model

    def validate(self, user_answer: str, standard_answer: str) -> bool:
        """
        验证输入是否有效
        """
        if not user_answer or not standard_answer:
            return False

        if not self.api_key:
            logger.error("DeepSeek API key not configured")
            return False

        return True

    def get_method_name(self) -> str:
        return 'llm'

    def _build_prompt(self, question_title: str, user_answer: str, standard_answer: str) -> str:
        """
        构建提示词
        """
        prompt = f"""
你是一个严格的评分助手。请评估用户答案的分数。

问题：{question_title}
标准答案：{standard_answer}
用户答案：{user_answer}

评分标准：
- 0-20分：答案完全错误或无关
- 21-40分：答案部分正确，但缺少关键点
- 41-60分：答案基本正确，但表述不够完整
- 61-80分：答案正确，表述清晰
- 81-95分：答案非常准确，表述优秀
- 96-100分：答案完美，完全匹配标准答案

请只输出分数（整数），不要添加任何解释。
"""
        return prompt

    def _call_llm_api(self, prompt: str) -> str:
        """
        调用 LLM API
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 10,
            "temperature": 0.0,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            response_data = response.json()
            llm_output = response_data["choices"][0]["message"]["content"].strip()

            logger.info(f"LLM API call successful: {llm_output}")
            return llm_output

        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API call failed: {e}")
            raise Exception(f"LLM API 请求失败: {str(e)}")

    def _parse_score(self, llm_output: str) -> float:
        """
        解析 LLM 输出的分数
        """
        match = re.search(r'\d+', llm_output)
        if match:
            score = float(match.group())
            return self.normalize_score(score)
        else:
            logger.warning(f"Could not parse score from LLM output: {llm_output}")
            return 0.0

    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict[str, Any]:
        """
        使用 LLM 计算分数
        """
        if not self.validate(user_answer, standard_answer):
            return {
                'score': 0.0,
                'details': {'error': '无效的输入或未配置 API 密钥'},
                'method': self.get_method_name()
            }

        try:
            question_title = kwargs.get('question_title', '未知题目')

            # 构建提示词
            prompt = self._build_prompt(question_title, user_answer, standard_answer)

            # 调用 LLM API
            llm_output = self._call_llm_api(prompt)

            # 解析分数
            final_score = self._parse_score(llm_output)

            details = {
                'llm_output': llm_output,
                'model': self.model,
                'question_title': question_title
            }

            logger.info(f"LLM scoring completed: {final_score}")
            return {
                'score': final_score,
                'details': details,
                'method': self.get_method_name()
            }

        except Exception as e:
            logger.error(f"LLM scoring failed: {e}", exc_info=True)
            return {
                'score': 0.0,
                'details': {'error': str(e)},
                'method': self.get_method_name()
            }
