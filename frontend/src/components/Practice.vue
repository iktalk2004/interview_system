<template>
  <div class="practice-container">
    <h2>答题练习</h2>

    <!-- 题目过滤和搜索 -->
    <el-form :model="filters" inline class="filter-form">
      <el-form-item label="搜索">
        <el-input v-model="filters.search" placeholder="标题" clearable @clear="fetchQuestions"/>
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-select v-model="filters.category" placeholder="选择分类" clearable style="width: 180px;">
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id"/>
        </el-select>
      </el-form-item>
      <el-form-item label="难度" prop="difficulty">
        <el-select v-model="filters.difficulty" placeholder="难度" clearable style="width: 180px;">
          <el-option
              v-for="(value, key) in difficultyMap"
              :key="key"
              :label="value"
              :value="key"
          />
        </el-select>
      </el-form-item>
      <el-button type="primary" @click="fetchQuestions">查询</el-button>
    </el-form>

    <!-- 题目列表表格 -->
    <el-table :data="questions" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" width="300"/>
      <el-table-column label="难度">
        <template #default="{ row }">
          {{ difficultyMap[row.difficulty] || '未知' }}
        </template>
      </el-table-column>
      <el-table-column prop="category.name" label="分类" width="150"/>
      <el-table-column label="状态" width="150">
        <template #default="{ row }">
          <el-tag v-if="getInteractionStatus(row.id)" :type="getInteractionStatus(row.id).type">
            {{ getInteractionStatus(row.id).text }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="goToPractice(row.id, null)">练习</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
        background v-if="total > 0"
        layout="prev, pager, next, total" :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        class="pagination"/>

    <!--    &lt;!&ndash; 历史记录抽屉 &ndash;&gt;-->
    <!--    <el-drawer v-model="showHistory" title="答题历史记录" direction="rtl" size="50%">-->
    <!--      <el-table :data="history" v-loading="loadingHistory">-->
    <!--        <el-table-column prop="question.title" label="题目"/>-->
    <!--        <el-table-column prop="score" label="评分"/>-->
    <!--        <el-table-column prop="time_spent" label="时长 (秒)"/>-->
    <!--        <el-table-column prop="created_at" label="时间" :formatter="formatDate"/>-->
    <!--        <el-table-column label="操作">-->
    <!--          <template #default="{ row }">-->
    <!--            <el-button-->
    <!--                size="small"-->
    <!--                @click="goToPractice(row.question?.id, row.id)"-->
    <!--                :disabled="!row.question?.id"-->
    <!--            >-->
    <!--              详情-->
    <!--            </el-button>-->
    <!--          </template>-->
    <!--        </el-table-column>-->
    <!--      </el-table>-->
    <!--    </el-drawer>-->

    <!--    &lt;!&ndash; 底部按钮：查看历史 &ndash;&gt;-->
    <!--    <el-button type="info" class="history-btn" @click="showHistory = true">查看历史记录</el-button>-->
  </div>
</template>

<script setup>
import {ref, reactive, onMounted, watch, computed} from 'vue'
import {useRouter} from 'vue-router'
import api from '@/api.js'
import {ElMessage} from 'element-plus'

const router = useRouter()


// 题目列表相关
const questions = ref([])
const categories = ref([])
const loading = ref(false)
const total = ref(0)  // 题目总数
const pageSize = 10
const currentPage = ref(1)

// 题目过滤参数
const filters = reactive({
  search: '',
  category: null,
  difficulty: null
})

// 难度标签映射
const difficultyMap = {1: '易', 2: '中', 3: '难',}

// 历史记录相关
const showHistory = ref(false)
const history = ref([])
const loadingHistory = ref(false)

// 交互状态缓存
const interactionStatusCache = ref({})

// 过滤后的分类，排除无效数据
const filteredCategories = computed(() => {
  return categories.value.filter(cat => cat && cat.id && cat.name)
})

// 获取题目列表
const fetchQuestions = async (page = 1) => {
  // 确保传递给fetchQuestions的是一个数字
  const pageNum = typeof page === 'number' ? page : parseInt(page) || 1;

  loading.value = true
  try {
    const params = {
      // 构建查询参数
      search: filters.search,
      category: filters.category,
      difficulty: filters.difficulty,
      page: pageNum,  // 当前页码
      page_size: pageSize  // 每页数量
    }

    const response = await api.get('questions/questions/', {params})

    questions.value = response.data.results || response.data
    total.value = response.data.count || questions.value.length
    currentPage.value = pageNum
    await updateInteractionStatus()
  } catch (err) {
    ElMessage.error('获取题目失败')
  } finally {
    loading.value = false
  }
}

// 获取分类
const fetchCategories = async () => {
  try {
    const response = await api.get('questions/categories/')
    // 后端返回id，name，parent 字段
    categories.value = response.data.results || response.data
  } catch (err) {
    ElMessage.error('获取分类失败')
  }
}

// 跳转到答题页,传递参数 questionId到答题页
const goToPractice = (questionId, interactionId) => {
  router.push({
    name: 'PracticeDetail',
    params: {id: questionId},  // 将这里的 id 改为路由中定义的参数名
    query: {interaction: interactionId}
  })
}

// 更新交互状态缓存
const updateInteractionStatus = async () => {
  try {
    const questionIds = questions.value.map(q => q.id).join(',')
    const response = await api.get('practice/interactions/', {params: {question__in: questionIds}})
    console.log(response)
    interactionStatusCache.value = {}
    response.data.forEach(int => {
      interactionStatusCache.value[int.question] = {
        type: int.score !== null ? 'success' : 'info',
        text: int.score !== null ? `已完成 (评分: ${int.score})` : '已开始'
      }
    })
    console.log('更新缓存', interactionStatusCache.value)
  } catch (err) {
    console.warn('状态更新失败')
  }
}

// 获取题目状态
const getInteractionStatus = (questionId) => {
  return interactionStatusCache.value[questionId] || {type: 'primary', text: '未练习'}
}

// 获取历史记录
const fetchHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await api.get('practice/interactions/history/')
    history.value = response.data
  } catch (err) {
    ElMessage.error('获取历史失败')
  } finally {
    loadingHistory.value = false
  }
}

// 日期格式化
const formatDate = (row) => {
  return new Date(row.created_at).toLocaleString()
}

// 分页处理
const handlePageChange = (page) => {
  currentPage.value = page
  fetchQuestions(page)
}

// 监听历史抽屉打开
watch(showHistory, (val) => {
  if (val) fetchHistory()
})

// 初始加载
onMounted(() => {
  fetchQuestions()
  fetchCategories()
})
</script>

<style scoped>
.practice-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
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

.history-btn {
  margin-top: 20px;
}

.loading {
  text-align: center;
  padding: 20px;
}
</style>