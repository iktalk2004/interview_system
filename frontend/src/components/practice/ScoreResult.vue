<template>
  <el-card class="result-card">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><CircleCheck /></el-icon>
        <span>答题结果</span>
      </div>
    </template>

    <div v-if="score !== null" class="score-section">
      <div class="final-score">
        <div class="score-label">最终评分</div>
        <div class="score-value">{{ displayScore }}</div>
        <el-rate 
          v-model="displayRating" 
          disabled 
          show-score 
          text-color="#ff9900" 
          score-template="{value}" 
        />
      </div>

      <div class="detail-scores" v-if="showDetails">
        <div class="detail-score-item" v-if="embeddingScore !== null">
          <div class="detail-label">嵌入模型评分</div>
          <div class="detail-value">{{ embeddingScore }}</div>
        </div>
        <div class="detail-score-item" v-if="deepseekScore !== null">
          <div class="detail-label">DeepSeek 评分</div>
          <div class="detail-value">{{ deepseekScore }}</div>
        </div>
      </div>

      <div class="score-feedback" v-if="feedback">
        <div class="feedback-label">评分反馈</div>
        <div class="feedback-content">{{ feedback }}</div>
      </div>
    </div>

    <div v-else class="no-score">
      <el-empty description="暂无评分" />
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { CircleCheck } from '@element-plus/icons-vue'

const props = defineProps({
  score: {
    type: Number,
    default: null
  },
  embeddingScore: {
    type: Number,
    default: null
  },
  deepseekScore: {
    type: Number,
    default: null
  },
  feedback: {
    type: String,
    default: ''
  },
  showDetails: {
    type: Boolean,
    default: true
  }
})

const displayScore = computed(() => {
  if (props.score === null) return 0
  return Math.round(props.score)
})

const displayRating = computed(() => {
  if (props.score === null) return 0
  return Math.ceil(props.score / 20)
})
</script>

<style scoped>
.result-card {
  margin-bottom: 20px;
  background: #1e1e1e;
  border: 1px solid #3c3c3c;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
  color: #67c23a;
}

.score-section {
  padding: 20px 0;
}

.final-score {
  text-align: center;
  margin-bottom: 30px;
}

.score-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.score-value {
  font-size: 48px;
  font-weight: bold;
  color: #61dafb;
  margin-bottom: 10px;
}

.detail-scores {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.detail-score-item {
  padding: 15px;
  background: #252525;
  border-radius: 4px;
  border-left: 3px solid #61dafb;
}

.detail-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.detail-value {
  font-size: 24px;
  font-weight: bold;
  color: #e0e0e0;
}

.score-feedback {
  padding: 15px;
  background: #252525;
  border-radius: 4px;
  border-left: 3px solid #e6a23c;
}

.feedback-label {
  font-size: 14px;
  font-weight: bold;
  color: #e6a23c;
  margin-bottom: 10px;
}

.feedback-content {
  line-height: 1.6;
  color: #e0e0e0;
}

.no-score {
  padding: 40px 0;
  text-align: center;
}
</style>
