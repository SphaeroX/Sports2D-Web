<template>
  <div class="home">
    <h1>{{ $t('home.title') }}</h1>
    <p class="subtitle">{{ $t('home.subtitle') }}</p>

    <!-- Upload -->
    <section class="card">
      <h2>{{ $t('home.upload.title') }}</h2>
      <div
        class="dropzone"
        @dragover.prevent
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()"
      >
        <p v-if="!uploading">{{ $t('home.upload.dragText') }}</p>
        <p v-else>Uploading...</p>
        <input ref="fileInput" type="file" accept="video/*" hidden @change="onFileChange" />
      </div>
      <p class="hint">{{ $t('home.upload.maxSize', { size: 500, duration: 300 }) }}</p>
      <p v-if="uploadError" class="error">{{ uploadError }}</p>
    </section>

    <!-- Editor -->
    <section class="card" v-if="jobStore.previewUrl">
      <h2>{{ $t('home.editor.title') }}</h2>
      <VideoEditor
        :previewUrl="jobStore.previewUrl"
        :duration="jobStore.duration"
        v-model:segments="segments"
      />
    </section>

    <!-- Parameters -->
    <section class="card" v-if="jobStore.previewUrl">
      <h2>{{ $t('home.parameters.title') }}</h2>
      <ParameterForm v-model:params="params" v-model:expertMode="expertMode" />
    </section>

    <!-- Actions -->
    <section class="actions" v-if="jobStore.previewUrl">
      <button class="btn-primary" @click="startAnalysis" :disabled="processing">
        {{ processing ? $t('home.actions.processing') : $t('home.actions.startAnalysis') }}
      </button>
      <p v-if="processError" class="error">{{ processError }}</p>
    </section>

    <!-- Job Queue / History -->
    <section class="card" v-if="jobStore.jobHistory.length > 0">
      <h2>{{ $t('home.queue.title') }}</h2>
      <div class="queue-list">
        <div
          v-for="job in jobStore.jobHistory"
          :key="job.job_id"
          class="queue-item"
          :class="{ active: isJobActive(job.status) }"
        >
          <div class="queue-header">
            <span class="job-name">{{ job.original_filename || job.job_id }}</span>
            <span class="badge" :class="statusClass(job.status)">{{ $t(statusLabel(job.status)) }}</span>
          </div>
          <div class="queue-progress" v-if="isJobActive(job.status)">
            <div class="progress-bar"><div class="fill" :style="{ width: (job.progress_percent || 0) + '%' }"></div></div>
            <span class="progress-text">{{ job.progress_percent || 0 }}%</span>
          </div>
          <p v-if="job.message" class="queue-message">{{ job.message }}</p>
          <div class="queue-actions">
            <router-link :to="{ name: 'job', params: { jobId: job.job_id } }" class="btn-small">
              {{ $t('home.queue.viewDetails') }}
            </router-link>
            <a
              v-if="job.status === 'completed' && job.download_url"
              :href="job.download_url"
              class="btn-small btn-green"
              download
              @click="onDownload(job.job_id)"
            >
              {{ $t('job.download') }}
            </a>
            <button class="btn-small danger" @click="deleteJob(job.job_id)">
              {{ $t('home.queue.delete') }}
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useJobStore, loadJobHistory, saveJobHistory } from '../stores/job.js'
import VideoEditor from '../components/VideoEditor.vue'
import ParameterForm from '../components/ParameterForm.vue'

const router = useRouter()
const jobStore = useJobStore()

const fileInput = ref(null)
const uploading = ref(false)
const uploadError = ref('')
const processError = ref('')
const processing = ref(false)
const segments = ref([])
const params = ref({})
const expertMode = ref(false)

async function onDrop(e) {
  const files = e.dataTransfer.files
  if (files.length) await handleFile(files[0])
}
async function onFileChange(e) {
  const files = e.target.files
  if (files.length) await handleFile(files[0])
}
async function handleFile(file) {
  uploadError.value = ''
  uploading.value = true
  try {
    await jobStore.uploadVideo(file)
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

function resetForm() {
  segments.value = []
  params.value = {}
  expertMode.value = false
  uploadError.value = ''
  processError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  jobStore.reset()
}

async function startAnalysis() {
  processError.value = ''
  processing.value = true
  try {
    await jobStore.startProcessing(segments.value, params.value, expertMode.value)
    const startedJobId = jobStore.jobId
    resetForm()
    router.push({ name: 'job', params: { jobId: startedJobId } })
  } catch (err) {
    processError.value = err.response?.data?.detail || 'Failed to start processing'
  } finally {
    processing.value = false
  }
}

async function deleteJob(jobId) {
  if (!confirm('Delete this job?')) return
  try {
    await jobStore.deleteJob(jobId)
  } catch (err) {
    alert('Failed to delete job')
  }
}

function onDownload(jobId) {
  // Remove from local history after download starts
  setTimeout(() => {
    const history = loadJobHistory().filter(j => j.job_id !== jobId)
    saveJobHistory(history)
    jobStore.jobHistory = history
  }, 500)
}

function isJobActive(status) {
  return ['pending', 'preprocessing', 'queued', 'processing'].includes(status)
}

function statusLabel(status) {
  const map = {
    pending: 'job.states.pending',
    preprocessing: 'job.states.preprocessing',
    queued: 'job.states.queued',
    processing: 'job.states.processing',
    completed: 'job.states.completed',
    failed: 'job.states.failed',
  }
  return map[status] || status
}

function statusClass(status) {
  const map = {
    pending: 'gray',
    preprocessing: 'blue',
    queued: 'blue',
    processing: 'blue',
    completed: 'green',
    failed: 'red',
  }
  return map[status] || 'gray'
}

onMounted(() => {
  jobStore.startHistoryPolling()
})

onUnmounted(() => {
  jobStore.stopHistoryPolling()
})
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: 1.5rem; }
.subtitle { color: #94a3b8; margin-bottom: 0.5rem; }
.card {
  background: #1e293b; border: 1px solid #334155; border-radius: 12px;
  padding: 1.5rem;
}
.card h2 { font-size: 1.1rem; margin-bottom: 1rem; color: #38bdf8; }
.dropzone {
  border: 2px dashed #475569; border-radius: 10px; padding: 2rem;
  text-align: center; cursor: pointer; color: #94a3b8; transition: border-color 0.2s;
}
.dropzone:hover { border-color: #38bdf8; color: #e2e8f0; }
.hint { font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; }
.error { color: #f87171; margin-top: 0.5rem; }
.actions { text-align: center; }
.btn-primary {
  background: #0ea5e9; color: #fff; border: none; padding: 0.8rem 2rem;
  border-radius: 8px; font-size: 1rem; cursor: pointer; font-weight: 600;
}
.btn-primary:disabled { background: #334155; cursor: not-allowed; }
.btn-primary:hover:not(:disabled) { background: #0284c7; }

/* Queue styles */
.queue-list { display: flex; flex-direction: column; gap: 1rem; }
.queue-item {
  background: #0f172a; border: 1px solid #334155; border-radius: 8px;
  padding: 1rem; transition: border-color 0.2s;
}
.queue-item.active { border-color: #0ea5e9; }
.queue-header {
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;
}
.job-name { font-weight: 600; color: #e2e8f0; font-size: 0.95rem; word-break: break-all; }
.badge { padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }
.badge.gray { background: #334155; color: #cbd5e1; }
.badge.blue { background: #0ea5e9; color: #fff; }
.badge.green { background: #22c55e; color: #fff; }
.badge.red { background: #ef4444; color: #fff; }
.queue-progress {
  display: flex; align-items: center; gap: 0.6rem; margin-top: 0.8rem;
}
.progress-bar { flex: 1; height: 8px; background: #334155; border-radius: 999px; overflow: hidden; }
.fill { height: 100%; background: #0ea5e9; transition: width 0.3s; }
.progress-text { font-size: 0.8rem; color: #94a3b8; min-width: 36px; text-align: right; }
.queue-message { color: #94a3b8; font-size: 0.85rem; margin-top: 0.4rem; }
.queue-actions {
  display: flex; gap: 0.5rem; margin-top: 0.8rem;
}
.btn-small {
  background: #334155; color: #e2e8f0; border: none; padding: 0.4rem 0.8rem;
  border-radius: 6px; font-size: 0.8rem; cursor: pointer; text-decoration: none; display: inline-block;
}
.btn-small:hover { background: #475569; }
.btn-green { background: #22c55e; color: #fff; }
.btn-green:hover { background: #16a34a; }
.btn-small.danger { background: #ef4444; color: #fff; }
.btn-small.danger:hover { background: #dc2626; }
</style>
