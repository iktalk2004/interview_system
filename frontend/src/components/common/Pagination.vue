<template>
  <div class="pagination-container">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="total"
      :background="true"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  total: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    default: 10
  },
  currentPage: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:page-size', 'update:current-page', 'change'])

const localPageSize = ref(props.pageSize)
const localCurrentPage = ref(props.currentPage)

watch(() => props.pageSize, (newSize) => {
  localPageSize.value = newSize
})

watch(() => props.currentPage, (newPage) => {
  localCurrentPage.value = newPage
})

function handleSizeChange(size) {
  localPageSize.value = size
  emit('update:page-size', size)
  emit('change', { page: localCurrentPage.value, pageSize: size })
}

function handleCurrentChange(page) {
  localCurrentPage.value = page
  emit('update:current-page', page)
  emit('change', { page, pageSize: localPageSize.value })
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 0;
  margin-top: 24px;
}

.pagination-container :deep(.el-pagination) {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.pagination-container :deep(.el-pagination.is-background .el-pager li) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.pagination-container :deep(.el-pagination.is-background .el-pager li:hover) {
  transform: translateY(-2px);
}

.pagination-container :deep(.el-pagination.is-background .el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.pagination-container :deep(.el-pagination .btn-prev),
.pagination-container :deep(.el-pagination .btn-next) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.pagination-container :deep(.el-pagination .btn-prev:hover),
.pagination-container :deep(.el-pagination .btn-next:hover) {
  transform: translateY(-2px);
}

.pagination-container :deep(.el-pagination__sizes),
.pagination-container :deep(.el-pagination__jump) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #606266;
}

@media (max-width: 768px) {
  .pagination-container :deep(.el-pagination) {
    gap: 4px;
  }

  .pagination-container :deep(.el-pagination__total),
  .pagination-container :deep(.el-pagination__sizes) {
    display: none;
  }

  .pagination-container :deep(.el-pagination__jump) {
    order: -1;
  }
}
</style>
