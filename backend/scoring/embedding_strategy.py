from .strategies import ScoringStrategy
from typing import Dict, Any
import math
import re
import logging

logger = logging.getLogger(__name__)


class EmbeddingScoringStrategy(ScoringStrategy):
    """
    基于嵌入模型的评分策略
    使用句子嵌入计算语义相似度
    """

    def __init__(self, model_name='DMetaSoul/sbert-chinese-general-v2'):
        self.model_name = model_name
        self._model = None
        self._model_load_error = None

    def get_model(self):
        """
        获取嵌入模型（懒加载）
        """
        if self._model is not None:
            return self._model

        if self._model_load_error is not None:
            raise Exception(self._model_load_error)

        try:
            from sentence_transformers import SentenceTransformer
            from django.core.cache import cache

            model = SentenceTransformer(self.model_name)
            self._model = model
            logger.info(f"Embedding model {self.model_name} loaded successfully")
            return model
        except Exception as e:
            self._model_load_error = str(e)
            logger.error(f"Failed to load embedding model: {e}")
            raise Exception(f"模型加载失败: {str(e)}")

    def validate(self, user_answer: str, standard_answer: str) -> bool:
        """
        验证输入是否有效
        """
        if not user_answer or not standard_answer:
            return False
        return True

    def get_method_name(self) -> str:
        return 'embedding'

    def preprocess(self, text: str) -> str:
        """
        预处理文本
        """
        text = re.sub(r'[^\u4e00-\u9fa5\w\s]', '', text)
        text = ' '.join(text.split())
        return text.lower()

    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict[str, Any]:
        """
        使用嵌入模型计算分数
        """
        if not self.validate(user_answer, standard_answer):
            return {
                'score': 0.0,
                'details': {'error': '无效的输入'},
                'method': self.get_method_name()
            }

        try:
            from sentence_transformers import util
            from django.core.cache import cache

            model = self.get_model()

            user_answer_processed = self.preprocess(user_answer)
            std_answer_processed = self.preprocess(standard_answer)

            # 最小长度检查
            if len(user_answer_processed) < 0.5 * len(std_answer_processed):
                score = 0.0
                details = {
                    'reason': '答案过短，缺少关键内容',
                    'user_answer_length': len(user_answer_processed),
                    'std_answer_length': len(std_answer_processed)
                }
                return {
                    'score': score,
                    'details': details,
                    'method': self.get_method_name()
                }

            # 缓存标准答案嵌入
            question_id = kwargs.get('question_id')
            if question_id:
                cache_key = f'question_embedding_{question_id}'
                std_embedding = cache.get(cache_key)
                if std_embedding is None:
                    std_embedding = model.encode(std_answer_processed)
                    cache.set(cache_key, std_embedding, timeout=86400)
            else:
                std_embedding = model.encode(std_answer_processed)

            # 用户嵌入
            user_embedding = model.encode(user_answer_processed)

            # 余弦相似度
            cos_sim = util.cos_sim(user_embedding, std_embedding)[0][0].item()

            # 长度惩罚
            len_penalty = max(0.5, 1 - abs(len(user_answer_processed) - len(std_answer_processed)) / max(len(user_answer_processed), len(std_answer_processed), 1))

            # 调整相似度
            adjusted_sim = cos_sim * len_penalty

            # 非线性映射：sigmoid
            if adjusted_sim < 0.3:
                sigmoid_score = 0
            else:
                sigmoid_score = 1 / (1 + math.exp(-6 * (adjusted_sim - 0.5)))

            # 标准化分数
            final_score = self.normalize_score(sigmoid_score * 100)

            details = {
                'cosine_similarity': float(cos_sim),
                'length_penalty': float(len_penalty),
                'adjusted_similarity': float(adjusted_sim),
                'sigmoid_score': float(sigmoid_score)
            }

            logger.info(f"Embedding scoring completed: {final_score}")
            return {
                'score': final_score,
                'details': details,
                'method': self.get_method_name()
            }

        except Exception as e:
            logger.error(f"Embedding scoring failed: {e}", exc_info=True)
            return {
                'score': 0.0,
                'details': {'error': str(e)},
                'method': self.get_method_name()
            }
