<template>
  <div class="stat-card" :class="`stat-card-${type}`">
    <div class="stat-icon" :class="`stat-icon-${type}`">
      <slot name="icon">
        <el-icon><DataBoard /></el-icon>
      </slot>
    </div>
    <div class="stat-info">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { DataBoard } from '@element-plus/icons-vue'

defineProps({
  value: {
    type: [Number, String],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger'].includes(value)
  }
})
</script>

<style scoped>
.stat-card {
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
  background: #ffffff;
  border: 1px solid #ebeef5;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-card-default {
  border-left: 4px solid #409eff;
}

.stat-card-primary {
  border-left: 4px solid #409eff;
}

.stat-card-success {
  border-left: 4px solid #67c23a;
}

.stat-card-warning {
  border-left: 4px solid #e6a23c;
}

.stat-card-danger {
  border-left: 4px solid #f56c6c;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon-default {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.stat-icon-primary {
  background: linear-gradient(135deg, #409eff 0%, #53a8ff 100%);
  color: #ffffff;
}

.stat-icon-success {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: #ffffff;
}

.stat-icon-warning {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
  color: #ffffff;
}

.stat-icon-danger {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
  color: #ffffff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

@media (max-width: 768px) {
  .stat-value {
    font-size: 24px;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    font-size: 24px;
  }
}
</style>
