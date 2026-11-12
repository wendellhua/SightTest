<script setup lang="ts">
import { deleteProject, listProjects, type Project } from '@/api/project'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const projects = ref<Project[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await listProjects()
    projects.value = res.data.items
  } finally {
    loading.value = false
  }
}

async function onDelete(project: Project) {
  await ElMessageBox.confirm(`确定删除项目「${project.name}」？将删除全部项目数据。`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteProject(project.id)
  ElMessage.success('已删除')
  await load()
}

function goCreate() {
  router.push('/create-project')
}

function goProject(project: Project) {
  router.push(`/project/${project.id}`)
}

onMounted(load)
</script>

<template>
  <div class="projects">
    <div class="toolbar">
      <h2>我的项目</h2>
      <el-button type="primary" @click="goCreate">创建项目</el-button>
    </div>

    <el-empty v-if="!loading && projects.length === 0" description="还没有项目，点击右上角「创建项目」开始" />

    <div v-else v-loading="loading" class="grid">
      <div v-for="p in projects" :key="p.id" class="proj-card">
        <div class="proj-name">{{ p.name }}</div>
        <div class="proj-url" :title="p.url">{{ p.url }}</div>
        <div class="proj-meta">
          <el-tag size="small">{{ p.plan_status }}</el-tag>
        </div>
        <div class="proj-actions">
          <el-button size="small" type="primary" plain @click="goProject(p)">进入项目</el-button>
          <el-button size="small" type="danger" plain @click="onDelete(p)">删除</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.toolbar h2 {
  margin: 0;
  font-size: 20px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.proj-card {
  padding: 20px;
  background: #ffffff;
  border: 1px solid var(--st-border);
  border-radius: 12px;
}
.proj-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}
.proj-url {
  color: var(--st-text-2);
  font-size: 13px;
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.proj-meta {
  margin-bottom: 16px;
}
.proj-actions {
  display: flex;
  gap: 8px;
}
</style>
