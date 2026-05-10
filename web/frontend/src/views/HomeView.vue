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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useJobStore } from '../stores/job.js'
import VideoEditor from '../components/VideoEditor.vue'
import ParameterForm from '../components/ParameterForm.vue'

const router = useRouter()
const jobStore = useJobStore()

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
async function startAnalysis() {
  processError.value = ''
  processing.value = true
  try {
    await jobStore.startProcessing(segments.value, params.value, expertMode.value)
    router.push({ name: 'job', params: { jobId: jobStore.jobId } })
  } catch (err) {
    processError.value = err.response?.data?.detail || 'Failed to start processing'
  } finally {
    processing.value = false
  }
}
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
</style>
