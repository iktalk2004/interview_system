<template>
  <div class="practice-detail-container">
    <h2>{{ question.title || '加载中...' }}</h2>

    <div v-if="loading">加载中...</div>
    <div v-else-if="!question.id">
      <p>题目不存在或加载失败</p>
    </div>

    <!--答题界面-->
    <div v-else>
      <!-- 题目内容 -->
      <div class="question-content">
        <h3>题目描述：</h3>
        <p>{{ question.title }}</p>
      </div>

      <!-- 用户答案输入（如果未评分且未提交） -->
      <el-form ref="answerFormRef" :model="form" label-width="100px"
               v-if="interaction.score === null && !isSubmitted.value">
        <el-form-item label="你的答案" prop="answer">
          <el-input v-model="form.answer" type="textarea" :rows="8" placeholder="请输入你的答案"/>
        </el-form-item>
        <el-form-item label="评分方式" prop="scoringMethod">
          <el-select v-model="form.scoringMethod" placeholder="选择评分方式">
            <el-option label="嵌入模型" value="embedding"></el-option>
            <el-option label="DeepSeek" value="deepseek"></el-option>
            <el-option label="两者平均" value="both"></el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <!-- 计时器 -->
      <div class="timer">答题时长：{{ timeSpent }} 秒</div>

      <!-- 如果已提交，显示答案 -->
      <div v-if="isSubmitted.value">
        <h3>你的答案：</h3>
        <p>{{ interaction.answer }}</p>
      </div>

      <!-- 如果已评分，显示评分反馈和正确答案 -->
      <div v-if="interaction.score !== null">
        <h3 v-if="form.embeddingScore !== null">嵌入模型评分：</h3>
        <el-rate v-if="form.embeddingScore !== null" v-model="form.embeddingScore" disabled show-score
                 text-color="#ff9900" score-template="{value}"/>

        <h3 v-if="form.deepseekScore !== null">DeepSeek评分：</h3>
        <el-rate v-if="form.deepseekScore !== null" v-model="form.deepseekScore" disabled show-score
                 text-color="#ff9900" score-template="{value}"/>

        <h3 v-if="form.score !== null">最终评分：</h3>
        <el-rate v-if="form.score !== null" v-model="form.score" disabled show-score text-color="#ff9900"
                 score-template="{value}"/>
        <h3>你的答案：</h3>
        <p>{{ interaction.answer }}</p>
        <h3>正确答案：</h3>
        <p>{{ question.answer }}</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="goBack">返回列表</el-button>
      <el-button v-if="interaction.score !== null" type="warning" @click="resetAndRetry">重新答题</el-button>
      <el-button v-if="interaction.score === null && !isSubmitted.value" type="primary" :loading="submitting"
                 @click="submitAnswer">提交答案
      </el-button>
      <el-button type="info" @click="toggleFavorite"> {{ interaction.is_favorite ? '取消收藏' : '收藏' }}</el-button>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted, onUnmounted, watch} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import {ElMessage} from 'element-plus'
import {debounce} from "lodash";
import api from '@/api.js'

const router = useRouter()
const route = useRoute()

const questionId = route.params.id
const hasMeaningfulAction = ref(false)  // 标记是否为“有意义操作”（输入或浏览时间>10s）
const isSubmitted = ref(false)  // 跟踪is_submitted，初始从后端获取
const interactionIdQuery = route.query.interaction  // 如果从历史进入，带 interaction id

const question = ref({})
const interaction = reactive({
  id: null,
  score: null,
  answer: '',
  is_favorite: false,
  time_spent: 0,
  is_submitted: false // 新增初始化
})

const form = reactive({
  answer: '',
  score: null,
  embeddingScore: null,
  deepseekScore: null,
  scoringMethod: 'embedding' // 默认值
})

const loading = ref(true)
const submitting = ref(false)
const timeSpent = ref(0)
let timerInterval = null

// 加载题目和交互
const loadData = async () => {
  // 题目ID不能为空
  if (!questionId) {
    ElMessage.error('题目ID不能为空')
    goBack()
    return
  }

  loading.value = true
  try {
    // 获取题目
    const qResponse = await api.get(`questions/questions/${questionId}/`)
    question.value = qResponse.data.results || qResponse.data

    // 获取或创建交互
    let iResponse
    if (interactionIdQuery) {
      // 如果从历史记录进入，加载对应的交互记录
      iResponse = await api.get(`practice/interactions/${interactionIdQuery}/`)
    } else {
      iResponse = await api.get('practice/interactions/', {params: {question: questionId}})
      if (Array.isArray(iResponse.data) && iResponse.data.length > 0) {
        iResponse = {data: iResponse.data[0]}  // 只取第一条（后端过滤未提交的）
      } else if (!Array.isArray(iResponse.data)) {
        iResponse = iResponse
      } else {
        // 返回空数组：不创建，设置为空
        iResponse = {data: {id: null, score: null, answer: '', time_spent: 0, is_favorite: false, is_submitted: false}}
      }
    }
    console.log('iResponse:', iResponse)
    Object.assign(interaction, iResponse.data)  // 用assign避免reactive覆盖


    form.answer = interaction.answer || ''
    form.score = interaction.score
    timeSpent.value = interaction.time_spent || 0
    isSubmitted.value = interaction.is_submitted || false

    console.log('iResponse data status:', iResponse.data.status)
    interaction.status = iResponse.data.status || ''
    console.log('interaction:', interaction.status)
    if (interaction.status === 'viewed') {
      timeSpent.value = 0  // 重置，不累加浏览时长
    }

    if (interaction.score === undefined) interaction.score = null

    if (interaction.score === null) startTimer()

    // 如果已有记录，标记为有操作
    if (interaction.id) hasMeaningfulAction.value = true
  } catch (err) {
    console.error('加载失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '加载失败')
    goBack()
  } finally {
    loading.value = false
  }
}

// 处理浏览记录
const saveViewRecord = async () => {
  const data = {
    question: questionId,
    time_spent: timeSpent.value,
    is_submitted: false,
    status: 'viewed'  // 可选标记浏览
  }

  try {
    const response = await api.post('practice/interactions/', data)
    // 不需更新本地interaction（页面已卸载）
  } catch (err) {
    console.error('保存浏览记录失败:', err)
    // 静默失败，避免打扰
  }
}

// 监听答案变化，debounce自动保存草稿
watch(() => form.answer, debounce(async (newVal) => {
  if (newVal && !isSubmitted.value) {
    hasMeaningfulAction.value = true
    await saveDraft()
  }
}, 3000)) // 3s防抖

// 提交答案
const submitAnswer = async () => {
  if (!form.answer) {
    ElMessage.warning('请输入答案')
    return
  }
  if (!form.scoringMethod) {
    ElMessage.warning('请选择评分方式')
    return
  }

  submitting.value = true
  stopTimer()

  const data = {
    question: questionId,  // 以防无id
    answer: form.answer,
    time_spent: timeSpent.value,
    is_submitted: true  // 标记已提交（修正字段名）
  }

  try {
    let response
    if (interaction.id) {
      response = await api.patch(`practice/interactions/${interaction.id}/`, data)
    } else {
      response = await api.post('practice/interactions/', data)
      interaction.id = response.data.id
    }
    Object.assign(interaction, response.data)
    isSubmitted.value = true
    hasMeaningfulAction.value = true
    ElMessage.success('答案提交成功')

    // 根据选择的评分方式获取评分
    await getScoreByMethod()
  } catch (err) {
    console.error('提交失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '提交失败')
  } finally {
    submitting.value = false
  }
}


// 重置交互状态并重新答题
const resetAndRetry = async () => {
  if (!interaction.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  try {
    const response = await api.post(`practice/interactions/${interaction.id}/reset_interaction/`)
    ElMessage.success(response.data.message)

    // 重置本地状态
    form.answer = ''
    form.score = null
    form.embeddingScore = null
    form.deepseekScore = null
    interaction.score = null
    interaction.answer = ''
    interaction.is_submitted = false
    interaction.status = 'draft'
    isSubmitted.value = false

    // 重启计时器
    startTimer()
    hasMeaningfulAction.value = true

  } catch (err) {
    console.error('重置失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '重置失败')
  }
}
// 保存草稿
const saveDraft = async () => {
  if (!form.answer) return // 忽略空答案

  const data = {
    question: questionId,
    answer: form.answer,
    time_spent: timeSpent.value,
    is_submitted: false,  // 草稿
    status: 'draft'
  }

  try {
    let response
    if (interaction.id) {
      // 如果已存在交互，更新
      response = await api.patch(`practice/interactions/${interaction.id}/`, data)
    } else {
      // 创建交互
      response = await api.post('practice/interactions/', data)
      interaction.id = response.data.id
    }
    Object.assign(interaction, response.data)  // 更新本地
    ElMessage.success('草稿已自动保存')
  } catch (err) {
    console.error('保存草稿失败:', err)
    ElMessage.error('保存草稿失败')
  }
}

// 根据方法获取评分
const getScoreByMethod = async () => {
  if (!interaction.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  if (!interaction.answer) {
    ElMessage.warning('请先提交答案')
    return
  }

  try {
    form.embeddingScore = null
    form.deepseekScore = null
    form.score = null

    if (form.scoringMethod === 'embedding' || form.scoringMethod === 'both') {
      const embeddingResponse = await api.post(`practice/interactions/${interaction.id}/embedding_score/`)
      form.embeddingScore = embeddingResponse.data.score
      ElMessage.success(`嵌入模型评分：${form.embeddingScore}`)
    }

    if (form.scoringMethod === 'deepseek' || form.scoringMethod === 'both') {
      const deepseekResponse = await api.post(`practice/interactions/${interaction.id}/deepseek_score/`)
      form.deepseekScore = deepseekResponse.data.score
      ElMessage.success(`DeepSeek评分：${form.deepseekScore}`)
    }

    // 计算最终分数
    if (form.scoringMethod === 'both') {
      let finalScore = Math.round((form.embeddingScore + form.deepseekScore) / 2 * 10) / 10;  // 保留一位小数
      if (finalScore >= 95) {
        finalScore = 100;
      }
      form.score = finalScore
      interaction.score = finalScore
    } else if (form.scoringMethod === 'embedding') {
      form.score = form.embeddingScore
      interaction.score = form.embeddingScore
    } else if (form.scoringMethod === 'deepseek') {
      form.score = form.deepseekScore
      interaction.score = form.deepseekScore
    }

    // 可选：更新到后端
    await api.patch(`practice/interactions/${interaction.id}/`, {score: form.score})
  } catch (err) {
    console.error('评分失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '评分失败')
  }
}

// 切换收藏
const toggleFavorite = async () => {
  if (!interaction.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  try {
    const response = await api.post(`practice/interactions/${interaction.id}/favorite/`)
    interaction.is_favorite = response.data.is_favorite
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

// 开始计时
const startTimer = () => {
  timerInterval = setInterval(() => timeSpent.value++, 1000)
}

// 停止计时
const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

// 卸载停止计时
onUnmounted(() => {
  stopTimer()
  if (hasMeaningfulAction.value) {
    // 已输入/提交：已在watch/submit中保存，无需重复
  } else if (timeSpent.value > 10 && !form.answer.trim() && !isSubmitted.value) {
    // 纯浏览>10s：创建浏览记录（加 trim()）
    saveViewRecord()
  }
  // <10s 或有输入但未debounce：不保存，丢弃
})

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