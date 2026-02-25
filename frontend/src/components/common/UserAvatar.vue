<template>
  <div class="user-avatar" :class="[`size-${size}`, { clickable: clickable }]" @click="handleClick">
    <img
      v-if="avatarUrl"
      :src="avatarUrl"
      :alt="username"
      class="avatar-image"
      @error="handleImageError"
    />
    <div v-else class="avatar-placeholder">
      <el-icon><User /></el-icon>
    </div>
    <div v-if="showBadge && badgeCount > 0" class="avatar-badge">
      {{ badgeCount > 99 ? '99+' : badgeCount }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { User } from '@element-plus/icons-vue'

const props = defineProps({
  user: {
    type: Object,
    default: null
  },
  avatarUrl: {
    type: String,
    default: ''
  },
  username: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large', 'xlarge'].includes(value)
  },
  clickable: {
    type: Boolean,
    default: false
  },
  showBadge: {
    type: Boolean,
    default: false
  },
  badgeCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['click'])

const displayAvatarUrl = computed(() => {
  if (props.avatarUrl) return props.avatarUrl
  if (props.user?.avatar_url) return props.user.avatar_url
  return '/media/avatars/default/default-avatar.svg'
})

function handleClick() {
  if (props.clickable) {
    emit('click', props.user)
  }
}

function handleImageError(event) {
  event.target.style.display = 'none'
  event.target.nextElementSibling.style.display = 'flex'
}
</script>

<style scoped>
.user-avatar {
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  background: #1e1e1e;
  border: 2px solid #3c3c3c;
  display: inline-block;
}

.user-avatar.clickable {
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-avatar.clickable:hover {
  border-color: #61dafb;
  transform: scale(1.05);
}

.size-small {
  width: 32px;
  height: 32px;
}

.size-medium {
  width: 48px;
  height: 48px;
}

.size-large {
  width: 64px;
  height: 64px;
}

.size-xlarge {
  width: 96px;
  height: 96px;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: none;
  align-items: center;
  justify-content: center;
  color: #61dafb;
  font-size: 24px;
}

.size-small .avatar-placeholder {
  font-size: 16px;
}

.size-medium .avatar-placeholder {
  font-size: 24px;
}

.size-large .avatar-placeholder {
  font-size: 32px;
}

.size-xlarge .avatar-placeholder {
  font-size: 48px;
}

.avatar-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #f56c6c;
  color: white;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: bold;
  min-width: 18px;
  text-align: center;
  border: 2px solid #1e1e1e;
}
</style>
