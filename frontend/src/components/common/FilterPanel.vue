<template>
  <div class="filter-panel">
    <div class="filter-header">
      <h3 class="filter-title">
        <el-icon><Filter /></el-icon>
        筛选条件
      </h3>
      <el-button
        v-if="hasActiveFilters"
        link
        type="primary"
        @click="handleReset"
      >
        重置
      </el-button>
    </div>

    <div class="filter-content">
      <slot>
        <el-input
          v-model="localFilters.search"
          placeholder="搜索题目..."
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="localFilters.category"
          placeholder="选择分类"
          clearable
          @change="handleFilterChange"
        >
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>

        <el-select
          v-model="localFilters.difficulty"
          placeholder="选择难度"
          clearable
          @change="handleFilterChange"
        >
          <el-option label="简单" :value="1" />
          <el-option label="中等" :value="2" />
          <el-option label="困难" :value="3" />
          <el-option label="专家" :value="4" />
        </el-select>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Filter, Search } from '@element-plus/icons-vue'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  },
  categories: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:filters', 'search', 'filter-change', 'reset'])

const localFilters = ref({ ...props.filters })

const hasActiveFilters = computed(() => {
  return Object.values(localFilters.value).some(
    value => value !== null && value !== undefined && value !== ''
  )
})

watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

function handleSearch() {
  emit('update:filters', localFilters.value)
  emit('search', localFilters.value.search)
}

function handleFilterChange() {
  emit('update:filters', localFilters.value)
  emit('filter-change', localFilters.value)
}

function handleReset() {
  localFilters.value = {
    search: '',
    category: null,
    difficulty: null
  }
  emit('update:filters', localFilters.value)
  emit('reset')
}
</script>

<style scoped>
.filter-panel {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #ebeef5;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.filter-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-content :deep(.el-input),
.filter-content :deep(.el-select) {
  width: 100%;
}

@media (min-width: 768px) {
  .filter-content {
    flex-direction: row;
    align-items: center;
  }

  .filter-content :deep(.el-input) {
    flex: 2;
  }

  .filter-content :deep(.el-select) {
    flex: 1;
  }
}
</style>
