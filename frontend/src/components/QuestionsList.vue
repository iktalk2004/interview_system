<template>
  <div class="questions-container">
    <h2>题目库管理</h2>

    <!-- 搜索和过滤 -->
    <el-form inline>
      <el-form-item label="搜索">
        <el-input v-model="filters.search" placeholder="标题或内容" clearable/>
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="filters.category" placeholder="选择分类" clearable>
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id"/>
        </el-select>
      </el-form-item>
      <el-form-item label="难度">
        <el-select v-model="filters.difficulty" placeholder="难度" clearable>
          <el-option
              v-for="(value, key) in difficultyMap"
              :key="key"
              :label="value"
              :value="key"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="审核状态">
        <el-select v-model="filters.is_approved" placeholder="审核状态" clearable>
          <el-option label="已审核" :value="true"/>
          <el-option label="未审核" :value="false"/>
        </el-select>
      </el-form-item>
      <el-button type="primary" @click="fetchQuestions">查询</el-button>
      <el-button type="success" @click="openForm(null)">添加题目</el-button>
    </el-form>

    <!-- 题目表格 -->
    <el-table :data="questions" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题"/>
      <el-table-column label="难度">
        <template #default="{ row}">
          {{ difficultyMap[row.difficulty] || '未知' }}
        </template>
      </el-table-column>
      <el-table-column prop="category.name" label="分类"/>
      <el-table-column prop="is_approved" label="审核状态">
        <template #default="{ row }">
          <el-tag :type="row.is_approved ? 'success' : 'warning'">{{ row.is_approved ? '已审核' : '待审核' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="openForm(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteQuestion(row.id)">删除</el-button>
          <el-button v-if="!row.is_approved && isAdmin" size="small" type="primary" @click="approveQuestion(row.id)">
            审核通过
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination v-if="total > 0" layout="prev, pager, next" :total="total" :page-size="pageSize"
                   @current-change="handlePageChange"/>

    <!-- 编辑弹窗 -->
    <QuestionForm v-model="showForm" :question="selectedQuestion" @saved="fetchQuestions"/>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import api from '@/api.js'
import QuestionForm from './QuestionForm.vue'  // 导入表单组件

const questions = ref([])
const categories = ref([])  // 分类列表
const loading = ref(false)
const total = ref(0)
const pageSize = 10
const currentPage = ref(1)
const filters = reactive({
  search: '',
  category: null,
  difficulty: null,
  is_approved: null
})
const showForm = ref(false)
const selectedQuestion = ref(null)
const isAdmin = ref(false)  // 假设从 user info 获取，e.g., localStorage 或 API

const difficultyMap = {
  1: '易',
  2: '中',
  3: '难',
  // 可扩展更多
}

// 获取题目列表
const fetchQuestions = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      search: filters.search,
      category: filters.category,
      difficulty: filters.difficulty,
      is_approved: filters.is_approved,
      page,
      page_size: pageSize
    }
    const response = await api.get('questions/questions/', {params})
    console.log(response.data)
    questions.value = response.data.results || response.data
    total.value = response.data.count || questions.value.length
    currentPage.value = page
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
    categories.value = response.data
  } catch (err) {
    ElMessage.error('获取分类失败')
  }
}

// 删除题目
const deleteQuestion = async (id) => {
  ElMessageBox.confirm('确认删除？', '警告', {type: 'warning'}).then(async () => {
    try {
      await api.delete(`questions/questions/${id}/`)
      ElMessage.success('删除成功')
      fetchQuestions(currentPage.value)
    } catch (err) {
      ElMessage.error('删除失败')
    }
  })
}

// 审核通过
const approveQuestion = async (id) => {
  try {
    await api.patch(`questions/questions/${id}/`, {is_approved: true})
    ElMessage.success('审核通过')
    fetchQuestions(currentPage.value)
  } catch (err) {
    ElMessage.error('审核失败')
  }
}

// 打开表单
const openForm = (question) => {
  selectedQuestion.value = question ? {...question} : null
  showForm.value = true
}

// 分页
const handlePageChange = (page) => fetchQuestions(page)

onMounted(() => {
  fetchQuestions()
  fetchCategories()
  // 检查 isAdmin，从 profile API 或 localStorage
  // 示例：api.get('users/profile/').then(res => isAdmin.value = res.data.is_staff)
})
</script>

<style scoped>
.questions-container {
  padding: 20px;
}
</style>