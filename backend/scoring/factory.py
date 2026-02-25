from .strategies import ScoringStrategy
from .embedding_strategy import EmbeddingScoringStrategy
from .llm_strategy import LLMScoringStrategy
from typing import Dict, Type
import os
import logging

logger = logging.getLogger(__name__)


class ScoringStrategyFactory:
    """
    评分策略工厂类
    负责创建和管理评分策略实例
    """

    _strategies: Dict[str, Type[ScoringStrategy]] = {}
    _instances: Dict[str, ScoringStrategy] = {}

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[ScoringStrategy]):
        """
        注册评分策略

        Args:
            name: 策略名称
            strategy_class: 策略类
        """
        cls._strategies[name] = strategy_class
        logger.info(f"Registered scoring strategy: {name}")

    @classmethod
    def unregister_strategy(cls, name: str):
        """
        注销评分策略

        Args:
            name: 策略名称
        """
        if name in cls._strategies:
            del cls._strategies[name]
            logger.info(f"Unregistered scoring strategy: {name}")

    @classmethod
    def create_strategy(cls, name: str, **kwargs) -> ScoringStrategy:
        """
        创建评分策略实例

        Args:
            name: 策略名称
            **kwargs: 策略初始化参数

        Returns:
            ScoringStrategy: 策略实例

        Raises:
            ValueError: 策略不存在时抛出
        """
        if name not in cls._strategies:
            raise ValueError(f"Unknown scoring strategy: {name}")

        strategy_class = cls._strategies[name]
        instance = strategy_class(**kwargs)
        logger.info(f"Created scoring strategy instance: {name}")
        return instance

    @classmethod
    def get_strategy(cls, name: str, **kwargs) -> ScoringStrategy:
        """
        获取评分策略实例（单例模式）

        Args:
            name: 策略名称
            **kwargs: 策略初始化参数

        Returns:
            ScoringStrategy: 策略实例
        """
        if name not in cls._instances:
            cls._instances[name] = cls.create_strategy(name, **kwargs)

        return cls._instances[name]

    @classmethod
    def list_strategies(cls) -> list:
        """
        列出所有已注册的策略

        Returns:
            list: 策略名称列表
        """
        return list(cls._strategies.keys())

    @classmethod
    def clear_instances(cls):
        """
        清除所有策略实例
        """
        cls._instances.clear()
        logger.info("Cleared all scoring strategy instances")


# 注册默认策略
ScoringStrategyFactory.register_strategy('embedding', EmbeddingScoringStrategy)
ScoringStrategyFactory.register_strategy('llm', LLMScoringStrategy)


class ScoringContext:
    """
    评分上下文类
    负责协调评分策略的执行
    """

    def __init__(self, strategy_name: str = 'embedding'):
        """
        初始化评分上下文

        Args:
            strategy_name: 评分策略名称
        """
        self.strategy_name = strategy_name
        self._strategy = None

    def set_strategy(self, strategy_name: str):
        """
        设置评分策略

        Args:
            strategy_name: 评分策略名称
        """
        self.strategy_name = strategy_name
        self._strategy = None
        logger.info(f"Switched to scoring strategy: {strategy_name}")

    def get_strategy(self) -> ScoringStrategy:
        """
        获取当前评分策略

        Returns:
            ScoringStrategy: 策略实例
        """
        if self._strategy is None:
            self._strategy = ScoringStrategyFactory.get_strategy(self.strategy_name)

        return self._strategy

    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict:
        """
        执行评分

        Args:
            user_answer: 用户答案
            standard_answer: 标准答案
            **kwargs: 其他参数

        Returns:
            Dict: 评分结果
        """
        strategy = self.get_strategy()
        return strategy.score(user_answer, standard_answer, **kwargs)

    def validate(self, user_answer: str, standard_answer: str) -> bool:
        """
        验证输入

        Args:
            user_answer: 用户答案
            standard_answer: 标准答案

        Returns:
            bool: 输入是否有效
        """
        strategy = self.get_strategy()
        return strategy.validate(user_answer, standard_answer)

    def get_method_name(self) -> str:
        """
        获取当前评分方法名称

        Returns:
            str: 评分方法名称
        """
        return self.strategy_name


# 便捷函数
def create_scorer(strategy_name: str = 'embedding', **kwargs) -> ScoringContext:
    """
    创建评分器

    Args:
        strategy_name: 评分策略名称
        **kwargs: 策略初始化参数

    Returns:
        ScoringContext: 评分上下文实例
    """
    return ScoringContext(strategy_name)
