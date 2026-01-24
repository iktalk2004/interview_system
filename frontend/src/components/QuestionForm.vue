<template>
  <el-dialog v-model="visible" :title="question ? '编辑题目' : '添加题目'" width="600px" @close="resetForm">
    <el-form ref="formRef" :model="form" label-width="100px" :rules="rules">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入标题"/>
      </el-form-item>
      <el-form-item label="内容" prop="content">
        <el-input v-model="form.content" type="textarea" rows="4" placeholder="题目描述"/>
      </el-form-item>
      <el-form-item label="参考答案" prop="answer">
        <el-input v-model="form.answer" type="textarea" rows="4" placeholder="参考答案（可选）"/>
      </el-form-item>
      <el-form-item label="难度" prop="difficulty">
        <el-select v-model="form.difficulty" placeholder="选择难度">
          <el-option v-for="i in 5" :key="i" :label="i" :value="i"/>
        </el-select>
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-tree-select v-model="form.category" :data="categories" placeholder="选择分类"
                        :props="{ children: 'children', label: 'name' }" check-strictly/>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="saveQuestion">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import {ref, reactive, watch} from 'vue'
import api from '@/api.js'

const props = defineProps({
  question: Object
})
const emit = defineEmits(['saved'])

const visible = ref(false)
const saving = ref(false)
const formRef = ref(null)
const categories = ref([])  // 树状分类数据

const form = reactive({
  title: '',
  content: '',
  answer: '',
  difficulty: 1,
  category: null
})

const rules = reactive({
  title: [{required: true, message: '请输入标题'}],
  content: [{required: true, message: '请输入内容'}],
  difficulty: [{required: true, message: '选择难度'}],
  category: [{required: true, message: '选择分类'}]
})

// 监听 visible（v-model）
watch(() => visible.value, (val) => {
  if (!val) resetForm()
})

// 监听 props.question 填充表单
watch(() => props.question, (val) => {
  if (val) {
    Object.assign(form, val)
    form.category = val.category?.id
    visible.value = true
  }
}, {immediate: true})

// 获取树状分类（假设后端返回嵌套结构，如果平级需前端构建树）
const fetchCategories = async () => {
  try {
    const response = await api.get('questions/categories/')
    categories.value = buildTree(response.data)  // 假设 buildTree 函数构建树
  } catch (err) {
    ElMessage.error('获取分类失败')
  }
}

// 示例 buildTree（如果后端是平级）
function buildTree(data) {
  const map = {}
  data.forEach(item => {
    map[item.id] = {...item, children: []}
  })
  const tree = []
  data.forEach(item => {
    if (item.parent) map[item.parent].children.push(map[item.id])
    else tree.push(map[item.id])
  })
  return tree
}

// 保存
const saveQuestion = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (props.question) {
        await api.put(`questions/questions/${props.question.id}/`, form)
        ElMessage.success('更新成功')
      } else {
        await api.post('questions/questions/', form)
        ElMessage.success('添加成功')
      }
      emit('saved')
      visible.value = false
    } catch (err) {
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  })
}

// 重置
const resetForm = () => {
  formRef.value?.resetFields()
  Object.assign(form, {title: '', content: '', answer: '', difficulty: 1, category: null})
}

fetchCategories()  // 加载分类
</script>