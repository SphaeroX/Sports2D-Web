<template>
  <div class="job-view">
    <h1>{{ $t('job.title') }}</h1>
    <div class="card">
      <div class="status-row">
        <div>
          <strong>{{ $t('job.status') }}:</strong>
          <span class="badge" :class="statusClass">{{ $t(statusLabel) }}</span>
        </div>
        <div class="progress-wrap">
          <div class="progress-bar"><div class="fill" :style="{ width: progress + '%' }"></div></div>
          <span class="progress-text">{{ progress }}%</span>
        </div>
      </div>
      <p v-if="message" class="message">{{ message }}</p>

      <div v-if="isActive" class="link-box">
        <label>{{ $t('job.yourLink') }}</label>
        <div class="copy-row">
          <input readonly :value="currentUrl" />
          <button class="btn-small" @click="copyLink">{{ copied ? $t('job.copied') : $t('job.copyLink') }}</button>
        </div>
        <p class="hint">{{ $t('job.waitMessage') }}</p>
      </div>

      <div v-if="jobStore.status === 'completed' && jobStore.downloadUrl" class="download-box">
        <a :href="jobStore.downloadUrl" class="btn-primary" download @click="onDownload">{{ $t('job.download') }}</a>
        <p class="hint">{{ $t('job.downloadHint') }}</p>
        <p v-if="jobStore.resultSizeMb" class="hint">Size: {{ jobStore.resultSizeMb.toFixed(1) }} MB</p>
      </div>

      <div v-if="jobStore.status === 'failed'" class="error-box">
        <p>{{ jobStore.message || $t('errors.generic') }}</p>
      </div>

      <div class="actions-row">
        <button class="btn-small danger" @click="deleteAndGoHome">{{ $t('job.delete') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useJobStore } from '../stores/job.js'

const props = defineProps({ jobId: String })
const jobStore = useJobStore()
const router = useRouter()

const copied = ref(false)
const currentUrl = typeof window !== 'undefined' ? window.location.href : ''

async function deleteAndGoHome() {
  if (!confirm('Delete this job?')) return
  try {
    await jobStore.deleteJob(props.jobId)
    router.push({ name: 'home' })
  } catch (err) {
    alert('Failed to delete job')
  }
}

const statusLabel = computed(() => {
  const map = {
    pending: 'job.states.pending',
    preprocessing: 'job.states.preprocessing',
    queued: 'job.states.queued',
    processing: 'job.states.processing',
    completed: 'job.states.completed',
    failed: 'job.states.failed',
  }
  return jobStore.status ? map[jobStore.status] || jobStore.status : ''
})

const statusClass = computed(() => {
  const map = {
    pending: 'gray',
    preprocessing: 'blue',
    queued: 'blue',
    processing: 'blue',
    completed: 'green',
    failed: 'red',
  }
  return map[jobStore.status] || 'gray'
})

const isActive = computed(() => ['pending','preprocessing','queued','processing'].includes(jobStore.status))
const progress = computed(() => jobStore.progress || 0)
const message = computed(() => jobStore.message || '')

function copyLink() {
  navigator.clipboard.writeText(currentUrl)
  copied.value = true
  setTimeout(() => copied.value = false, 2000)
}

function onDownload() {
  setTimeout(() => {
    router.push({ name: 'home' })
  }, 500)
}

onMounted(() => {
  if (props.jobId && jobStore.jobId !== props.jobId) {
    jobStore.jobId = props.jobId
    jobStore.fetchStatus().then(() => {
      if (jobStore.status !== 'completed' && jobStore.status !== 'failed') {
        jobStore.startPolling()
      }
    })
  } else if (jobStore.jobId) {
    if (jobStore.status !== 'completed' && jobStore.status !== 'failed') {
      jobStore.startPolling()
    }
  }
})

onUnmounted(() => {
  jobStore.stopPolling()
})
</script>

<style scoped>
.job-view { max-width: 800px; margin: 0 auto; }
.card {
  background: #1e293b; border: 1px solid #334155; border-radius: 12px;
  padding: 1.5rem; margin-top: 1rem; display: flex; flex-direction: column; gap: 1.2rem;
}
.status-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
.badge { padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin-left: 0.5rem; }
.badge.gray { background: #334155; color: #cbd5e1; }
.badge.blue { background: #0ea5e9; color: #fff; }
.badge.green { background: #22c55e; color: #fff; }
.badge.red { background: #ef4444; color: #fff; }
.progress-wrap { display: flex; align-items: center; gap: 0.6rem; flex: 1; justify-content: flex-end; }
.progress-bar { width: 200px; height: 10px; background: #334155; border-radius: 999px; overflow: hidden; }
.fill { height: 100%; background: #0ea5e9; transition: width 0.3s; }
.progress-text { font-size: 0.85rem; color: #94a3b8; min-width: 36px; text-align: right; }
.message { color: #94a3b8; font-size: 0.9rem; }
.link-box label { display: block; font-weight: 600; margin-bottom: 0.4rem; }
.copy-row { display: flex; gap: 0.5rem; }
.copy-row input { flex: 1; background: #0f172a; border: 1px solid #334155; color: #e2e8f0; padding: 0.5rem; border-radius: 6px; }
.btn-small {
  background: #334155; color: #e2e8f0; border: none; padding: 0.5rem 0.9rem;
  border-radius: 6px; font-size: 0.85rem; cursor: pointer;
}
.hint { font-size: 0.8rem; color: #64748b; margin-top: 0.4rem; }
.download-box { text-align: center; }
.btn-primary {
  display: inline-block; background: #22c55e; color: #fff; text-decoration: none;
  padding: 0.8rem 2rem; border-radius: 8px; font-weight: 600; font-size: 1rem;
}
.error-box { color: #f87171; background: rgba(239,68,68,0.1); padding: 1rem; border-radius: 8px; }
.actions-row { display: flex; justify-content: flex-end; }
.btn-small.danger { background: #ef4444; color: #fff; }
</style>
