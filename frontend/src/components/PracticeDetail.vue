<template>
  <div class="practice-detail-container">
    <h2>{{ question.title || '加载中...' }}</h2>

    <div v-if="loading">加载中...</div>
    <div v-else-if="!question.id">
      <p>题目不存在或加载失败</p>
    </div>
    <div v-else>
      <!-- 题目内容 -->
      <div class="question-content">
        <h3>题目描述：</h3>
        <p>{{ question.answer || question.content }}</p>
      </div>

      <!-- 用户答案输入（如果未评分） -->
      <el-form ref="answerFormRef" :model="form" label-width="100px" v-if="interaction.score === null">
        <el-form-item label="你的答案" prop="answer">
          <el-input v-model="form.answer" type="textarea" :rows="8" placeholder="请输入你的答案"/>
        </el-form-item>
      </el-form>

      <!-- 计时器 -->
      <div class="timer">答题时长：{{ timeSpent }} 秒</div>

      <!-- 如果已提交，显示答案、评分和解析 -->
      <div v-if="interaction.score !== null">
        <h3>你的答案：</h3>
        <p>{{ interaction.answer }}</p>

        <h3>评分反馈：</h3>
        <el-rate v-model="form.score" disabled show-score text-color="#ff9900" score-template="{value}"/>

        <h3>正确答案：</h3>
        <p>{{ question.answer }}</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="goBack">返回列表</el-button>
      <el-button v-if="interaction.score === null" type="primary" :loading="submitting" @click="submitAnswer">提交答案
      </el-button>
      <el-button v-if="interaction.score === null && interaction.answer" type="success" @click="getScore">获取评分
      </el-button>
      <el-button type="info" @click="toggleFavorite"> {{ interaction.is_favorite ? '取消收藏' : '收藏' }}</el-button>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted, onUnmounted} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import api from '@/api.js'
import {ElMessage} from 'element-plus'

const router = useRouter()
const route = useRoute()

const questionId = route.params.id
const interactionIdQuery = route.query.interaction  // 如果从历史进入，带 interaction id

const question = ref({})
const interaction = ref({id: null, score: null, answer: '', is_favorite: false, time_spent: 0})
const form = reactive({
  answer: '',
  score: null
})
const loading = ref(true)
const submitting = ref(false)
const timeSpent = ref(0)
let timerInterval = null

// 加载题目和交互
const loadData = async () => {
  if (!questionId) {
    ElMessage.error('题目ID不能为空')
    goBack()
    return
  }

  loading.value = true
  try {
    // 获取题目
    const qResponse = await api.get(`questions/questions/${questionId}/`)
    question.value = qResponse.data

    // 获取或创建交互
    let iResponse
    if (interactionIdQuery) {
      iResponse = await api.get(`practice/interactions/${interactionIdQuery}/`)
    } else {
      iResponse = await api.get('practice/interactions/', {params: {question: questionId}})
      if (Array.isArray(iResponse.data) && iResponse.data.length === 0) {
        iResponse = await api.post('practice/interactions/', {question: questionId})
      } else if (Array.isArray(iResponse.data) && iResponse.data.length > 0) {
        iResponse = {data: iResponse.data[0]}
      } else if (!Array.isArray(iResponse.data)) {
        // 已经是对象格式
        iResponse = iResponse
      }
    }

    interaction.value = iResponse.data
    form.answer = interaction.value.answer || ''
    form.score = interaction.value.score
    timeSpent.value = interaction.value.time_spent || 0

    if (interaction.value.score === null) startTimer()
  } catch (err) {
    console.error('加载失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '加载失败')
    goBack()
  } finally {
    loading.value = false
  }
}

// 提交答案
const submitAnswer = async () => {
  if (!form.answer) {
    ElMessage.warning('请输入答案')
    return
  }

  if (!interaction.value.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  submitting.value = true
  stopTimer()

  try {
    const data = {
      answer: form.answer,
      time_spent: timeSpent.value
    }
    const response = await api.patch(`practice/interactions/${interaction.value.id}/`, data)
    interaction.value.answer = form.answer
    interaction.value.time_spent = timeSpent.value
    interaction.value.id = response.data.id  // 确保id被更新
    ElMessage.success('答案提交成功')
  } catch (err) {
    console.error('提交失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

// 获取评分
const getScore = async () => {
  if (!interaction.value.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  if (!interaction.value.answer) {
    ElMessage.warning('请先提交答案')
    return
  }

  try {
    const response = await api.post(`practice/interactions/${interaction.value.id}/score/`)
    form.score = response.data.score
    interaction.value.score = response.data.score
    ElMessage.success(`评分：${response.data.score}`)
  } catch (err) {
    console.error('评分失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '评分失败')
  }
}

// 切换收藏
const toggleFavorite = async () => {
  if (!interaction.value.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  try {
    const response = await api.post(`practice/interactions/${interaction.value.id}/favorite/`)
    interaction.value.is_favorite = response.data.is_favorite
    ElMessage.success(response.data.is_favorite ? '收藏成功' : '取消收藏')
  } catch (err) {
    console.error('操作失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '操作失败')
  }
}

// 返回列表
const goBack = () => {
  stopTimer()
  router.push({name: 'Practice'})
}

// 计时器
const startTimer = () => {
  timerInterval = setInterval(() => timeSpent.value++, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// 卸载停止计时
onUnmounted(() => stopTimer())

// 初始加载
onMounted(loadData)
</script>

<style scoped>
.practice-detail-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.question-content {
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.timer {
  text-align: right;
  color: #999;
  margin-bottom: 10px;
}

.actions {
  margin-top: 20px;
  text-align: right;
}
</style>
