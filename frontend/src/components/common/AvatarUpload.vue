<template>
  <div class="avatar-upload">
    <div class="avatar-preview" @click="triggerUpload">
      <UserAvatar
        :avatar-url="currentAvatarUrl"
        :username="username"
        size="large"
        :clickable="true"
      />
      <div class="upload-overlay">
        <el-icon><Camera /></el-icon>
        <span>{{ hasAvatar ? '更换头像' : '上传头像' }}</span>
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/gif,image/webp"
      style="display: none"
      @change="handleFileChange"
    />

    <div v-if="hasAvatar" class="avatar-actions">
      <el-button size="small" @click="triggerUpload">
        <el-icon><Upload /></el-icon>
        更换
      </el-button>
      <el-button size="small" type="danger" @click="handleDelete" :loading="deleting">
        <el-icon><Delete /></el-icon>
        删除
      </el-button>
    </div>

    <div class="upload-tips">
      <el-text size="small" type="info">
        支持 JPG、PNG、GIF、WebP 格式，文件大小不超过 2MB
      </el-text>
    </div>

    <el-dialog
      v-model="previewVisible"
      title="预览头像"
      width="400px"
      :before-close="handleClosePreview"
    >
      <div class="preview-container">
        <img :src="previewUrl" alt="预览" class="preview-image" />
      </div>
      <template #footer>
        <el-button @click="handleClosePreview">取消</el-button>
        <el-button type="primary" @click="handleConfirmUpload" :loading="uploading">
          确认上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Camera, Upload, Delete } from '@element-plus/icons-vue'
import UserAvatar from './UserAvatar.vue'
import api from '@/api'

const props = defineProps({
  avatarUrl: {
    type: String,
    default: ''
  },
  username: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['upload-success', 'delete-success'])

const fileInput = ref(null)
const previewVisible = ref(false)
const previewUrl = ref('')
const selectedFile = ref(null)
const uploading = ref(false)
const deleting = ref(false)

const currentAvatarUrl = computed(() => props.avatarUrl)
const hasAvatar = computed(() => !!props.avatarUrl)

function triggerUpload() {
  fileInput.value?.click()
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 2 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 2MB')
    return
  }

  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 JPG、PNG、GIF、WebP 格式的图片')
    return
  }

  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  previewVisible.value = true
}

function handleClosePreview() {
  previewVisible.value = false
  previewUrl.value = ''
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function handleConfirmUpload() {
  if (!selectedFile.value) return

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('avatar', selectedFile.value)

    const response = await api.post('users/profile/avatar/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    ElMessage.success('头像上传成功')
    emit('upload-success', response.data.avatar_url)
    handleClosePreview()
  } catch (error) {
    ElMessage.error('头像上传失败：' + (error.response?.data?.error || error.message))
  } finally {
    uploading.value = false
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除头像吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    deleting.value = true
    await api.delete('users/profile/avatar/delete/')

    ElMessage.success('头像删除成功')
    emit('delete-success')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('头像删除失败')
    }
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-preview:hover .upload-overlay {
  opacity: 1;
}

.upload-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
  gap: 8px;
}

.upload-overlay .el-icon {
  font-size: 24px;
}

.upload-overlay span {
  font-size: 12px;
}

.avatar-actions {
  display: flex;
  gap: 8px;
}

.upload-tips {
  text-align: center;
  max-width: 300px;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}
</style>
