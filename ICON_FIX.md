# 图标修复说明

## 已修复的图标问题

### 1. Memory 图标
- **问题**: Element Plus Icons 中没有 `Memory` 图标
- **修复**: 替换为 `Cpu` 图标
- **文件**: [CodePractice.vue](file:///e:\04_Interview_system\frontend\src\components\CodePractice.vue)

### 2. TrendCharts 图标
- **问题**: Element Plus Icons 中没有 `TrendCharts` 图标
- **修复**: 替换为 `DataLine` 图标
- **文件**: [Analytics.vue](file:///e:\04_Interview_system\frontend\src\components\Analytics.vue)

## 使用的图标列表

### CodePractice.vue
- `Search` - 搜索图标
- `Clock` - 时间图标
- `Cpu` - CPU/内存图标（替代 Memory）
- `Folder` - 文件夹图标

### CodePracticeDetail.vue
- `Star` - 星星图标（收藏）
- `Document` - 文档图标（笔记）
- `CircleCheck` - 圆形勾选图标
- `CircleClose` - 圆形关闭图标
- `Check` - 勾选图标
- `Close` - 关闭图标
- `Warning` - 警告图标

### NavBar.vue
- `Reading` - 阅读图标
- `HomeFilled` - 首页图标
- `Star` - 星星图标
- `Edit` - 编辑图标
- `Monitor` - 显示器图标（代码练习）
- `Document` - 文档图标
- `DataAnalysis` - 数据分析图标
- `Trophy` - 奖杯图标
- `Clock` - 时钟图标
- `User` - 用户图标
- `SwitchButton` - 切换按钮图标
- `ArrowDown` - 下箭头图标
- `Menu` - 菜单图标
- `Setting` - 设置图标
- `Close` - 关闭图标
- `Moon` - 月亮图标（深色模式）
- `Sunny` - 太阳图标（浅色模式）

### Analytics.vue
- `Refresh` - 刷新图标
- `Loading` - 加载图标
- `Document` - 文档图标
- `DataLine` - 数据线图标（替代 TrendCharts）
- `Clock` - 时钟图标
- `Star` - 星星图标

## Element Plus Icons 常用图标

以下是 Element Plus Icons 中可用的常用图标：

### 基础图标
- `Check` - 勾选
- `Close` - 关闭
- `CircleCheck` - 圆形勾选
- `CircleClose` - 圆形关闭
- `Warning` - 警告
- `InfoFilled` - 信息填充
- `SuccessFilled` - 成功填充
- `ErrorFilled` - 错误填充

### 导航图标
- `HomeFilled` - 首页
- `Menu` - 菜单
- `ArrowDown` - 下箭头
- `ArrowUp` - 上箭头
- `ArrowLeft` - 左箭头
- `ArrowRight` - 右箭头

### 操作图标
- `Search` - 搜索
- `Refresh` - 刷新
- `Loading` - 加载
- `Edit` - 编辑
- `Delete` - 删除
- `Plus` - 加号
- `Minus` - 减号

### 媒体图标
- `Monitor` - 显示器
- `Cpu` - CPU
- `Clock` - 时钟
- `Camera` - 相机
- `VideoCamera` - 摄像头

### 文件图标
- `Document` - 文档
- `Folder` - 文件夹
- `Download` - 下载
- `Upload` - 上传

### 用户图标
- `User` - 用户
- `Avatar` - 头像
- `Lock` - 锁
- `Unlock` - 解锁

### 系统图标
- `Setting` - 设置
- `Moon` - 月亮
- `Sunny` - 太阳
- `SwitchButton` - 切换按钮

### 数据图标
- `DataAnalysis` - 数据分析
- `DataLine` - 数据线
- `TrendCharts` - 趋势图（不存在，用 DataLine 替代）
- `PieChart` - 饼图
- `BarChart` - 柱状图

### 其他图标
- `Star` - 星星
- `Trophy` - 奖杯
- `Medal` - 奖牌
- `Message` - 消息
- `Bell` - 铃铛

## 如何查找正确的图标

### 方法1：查看官方文档
访问 Element Plus Icons 官方文档：
https://element-plus.org/zh-CN/component/icon.html

### 方法2：使用自动补全
在代码编辑器中输入：
```javascript
import {  } from '@element-plus/icons-vue'
```
然后使用自动补全查看所有可用的图标。

### 方法3：检查 node_modules
查看已安装的图标：
```bash
cd frontend/node_modules/@element-plus/icons-vue
ls
```

## 常见问题

### Q1: 如何添加新图标？
A: 直接从 `@element-plus/icons-vue` 导入即可：
```javascript
import { IconName } from '@element-plus/icons-vue'
```

### Q2: 图标不显示怎么办？
A: 确保已正确导入并在模板中使用：
```vue
<template>
  <el-icon><IconName /></el-icon>
</template>

<script setup>
import { IconName } from '@element-plus/icons-vue'
</script>
```

### Q3: 如何自定义图标大小？
A: 使用 CSS 或 Element Plus 的 size 属性：
```vue
<el-icon :size="20"><IconName /></el-icon>
```

### Q4: 如何自定义图标颜色？
A: 使用 CSS 类：
```vue
<el-icon class="custom-icon"><IconName /></el-icon>

<style scoped>
.custom-icon {
  color: var(--accent-primary);
}
</style>
```

## 总结

已修复的图标问题：
1. ✅ `Memory` → `Cpu`
2. ✅ `TrendCharts` → `DataLine`

所有图标现在都应该正常工作了！
