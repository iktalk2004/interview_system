<template>
  <div class="question-header">
    <el-button @click="$emit('back')" class="back-button" text>
      <el-icon><ArrowLeft /></el-icon>
      返回列表
    </el-button>
    <div class="header-info">
      <h1>{{ title || '加载中...' }}</h1>
      <div class="meta-tags">
        <el-tag v-if="category" type="info" size="small">
          <el-icon><Folder /></el-icon>
          {{ category.name }}
        </el-tag>
        <el-tag :type="difficultyType" size="small">
          <el-icon><Star /></el-icon>
          {{ difficultyText }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowLeft, Folder, Star } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  category: {
    type: Object,
    default: null
  },
  difficulty: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['back'])

const difficultyMap = {
  1: '简单',
  2: '中等',
  3: '困难',
  4: '专家'
}

const difficultyText = computed(() => difficultyMap[props.difficulty] || '未知')

const difficultyType = computed(() => {
  const types = {
    1: 'success',
    2: 'info',
    3: 'warning',
    4: 'danger'
  }
  return types[props.difficulty] || 'info'
})
</script>

<style scoped>
.question-header {
  margin-bottom: 20px;
}

.back-button {
  margin-bottom: 10px;
}

.header-info h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #e0e0e0;
}

.meta-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
