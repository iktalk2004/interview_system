<template>
  <div class="category-container">
    <h2>分类管理</h2>

    <!-- 添加根分类按钮 -->
    <el-button type="primary" icon="Plus" @click="addCategory(null)">添加根分类</el-button>

    <!-- 分类树 -->
    <el-tree
        :data="categories"
        node-key="id"
        draggable
        :props="{ children: 'children', label: 'name' }"
        @node-drop="handleDrop"
        v-loading="loading"
        class="category-tree"
    >
      <template #default="{ node, data }">
        <span class="node-label">{{ node.label }}</span>
        <div class="node-actions">
          <el-button size="small" type="success" icon="Plus" @click="addCategory(data.id)">添加子类</el-button>
          <el-button size="small" type="primary" icon="Edit" @click="editCategory(data)">编辑</el-button>
          <el-button size="small" type="danger" icon="Delete" @click="deleteCategory(data.id)">删除</el-button>
        </div>
      </template>
    </el-tree>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showForm" :title="selected ? '编辑分类' : '添加分类'" width="400px" center>
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="请输入分类名称" clearable/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForm = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, reactive} from 'vue'
import api from '@/api.js'
import {ElMessage, ElMessageBox} from "element-plus";

const categories = ref([])
const showForm = ref(false)
const selected = ref(null)
const form = reactive({name: '', parent: null})

function buildTree(data) {
  const map = {}
  data.forEach(item => {
    map[item.id] = {
      ...item,
      label: item.name,   // 添加 label 字段
      children: []
    }
  })
  const tree = []
  data.forEach(item => {
    if (item.parent) map[item.parent].children.push(map[item.id])
    else tree.push(map[item.id])
  })
  return tree
}


const fetchCategories = async () => {
  try {
    const response = await api.get('questions/categories/')
    categories.value = buildTree(response.data)  // 同上 buildTree
  } catch (err) {
    ElMessage.error('获取失败')
  }
}

const addCategory = (parentId) => {
  selected.value = null
  form.name = ''
  form.parent = parentId
  showForm.value = true
}

const editCategory = (data) => {
  selected.value = data
  form.name = data.name
  form.parent = data.parent?.id
  showForm.value = true
}

const saveCategory = async () => {
  try {
    if (selected.value) {
      await api.put(`questions/categories/${selected.value.id}/`, form)
    } else {
      await api.post('questions/categories/', form)
    }
    ElMessage.success('保存成功')
    showForm.value = false
    await fetchCategories()
  } catch (err) {
    ElMessage.error('保存失败')
  }
}

const deleteCategory = async (id) => {
  ElMessageBox.confirm('确认删除？', '警告').then(async () => {
    try {
      await api.delete(`questions/categories/${id}/`)
      ElMessage.success('删除成功')
      fetchCategories()
    } catch (err) {
      ElMessage.error('删除失败')
    }
  })
}

const handleDrop = async (draggingNode, dropNode, dropType) => {
  // 更新 parent（后端 patch）
  try {
    await api.patch(`questions/categories/${draggingNode.data.id}/`, {parent: dropType === 'inner' ? dropNode.data.id : dropNode.data.parent?.id})
    await fetchCategories()
  } catch (err) {
    ElMessage.error('拖拽失败')
  }
}

fetchCategories()
</script>

<style scoped>
.category-container {
  padding: 20px; /* 与 Questions.vue 一致 */
  background-color: #f9f9f9; /* 轻柔背景，提升美观 */
  border-radius: 8px; /* 圆角设计 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); /* 轻微阴影 */
}

.category-tree {
  margin-top: 20px;
  background-color: white;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
}

.node-label {
  font-weight: bold;
  color: #303133;
}

.node-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}
</style>