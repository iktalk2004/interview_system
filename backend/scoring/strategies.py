from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ScoringStrategy(ABC):
    """
    评分策略抽象基类
    定义所有评分策略必须实现的接口
    """

    @abstractmethod
    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict[str, Any]:
        """
        计算评分

        Args:
            user_answer: 用户答案
            standard_answer: 标准答案
            **kwargs: 其他参数

        Returns:
            Dict[str, Any]: 包含 score 和 details 的字典
            {
                'score': float,  # 评分结果 (0-100)
                'details': dict,  # 评分详情
                'method': str  # 评分方法名称
            }

        Raises:
            Exception: 评分失败时抛出异常
        """
        pass

    @abstractmethod
    def validate(self, user_answer: str, standard_answer: str) -> bool:
        """
        验证输入是否有效

        Args:
            user_answer: 用户答案
            standard_answer: 标准答案

        Returns:
            bool: 输入是否有效
        """
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        """
        获取评分方法名称

        Returns:
            str: 评分方法名称
        """
        pass

    def preprocess(self, text: str) -> str:
        """
        预处理文本（默认实现）

        Args:
            text: 待处理的文本

        Returns:
            str: 处理后的文本
        """
        import re
        text = re.sub(r'[^\u4e00-\u9fa5\w\s]', '', text)
        text = ' '.join(text.split())
        return text.lower()

    def normalize_score(self, score: float) -> float:
        """
        标准化分数到 0-100 范围

        Args:
            score: 原始分数

        Returns:
            float: 标准化后的分数 (0-100)
        """
        normalized = max(0, min(100, score))
        if normalized >= 95:
            normalized = 100
        return round(normalized, 1)
