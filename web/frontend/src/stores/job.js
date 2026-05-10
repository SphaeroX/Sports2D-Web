import { createPinia } from 'pinia'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = ''

export const useJobStore = defineStore('job', {
  state: () => ({
    jobId: null,
    previewUrl: null,
    duration: 0,
    status: null,
    progress: 0,
    message: '',
    downloadUrl: null,
    resultSizeMb: null,
    pollingInterval: null,
  }),
  actions: {
    async uploadVideo(file) {
      const form = new FormData()
      form.append('file', file)
      const res = await axios.post(`${API_BASE}/api/upload/`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      this.jobId = res.data.job_id
      this.previewUrl = res.data.preview_url
      this.duration = res.data.original_duration
      this.status = 'pending'
      return res.data
    },
    async startProcessing(segments, params, expertMode) {
      const res = await axios.post(`${API_BASE}/api/jobs/process`, {
        job_id: this.jobId,
        segments,
        params,
        expert_mode: expertMode,
      })
      this.status = 'queued'
      return res.data
    },
    async fetchStatus() {
      if (!this.jobId) return
      const res = await axios.get(`${API_BASE}/api/jobs/${this.jobId}/status`)
      const d = res.data
      this.status = d.status
      this.progress = d.progress_percent
      this.message = d.message || ''
      this.downloadUrl = d.download_url
      this.resultSizeMb = d.result_size_mb
      return d
    },
    startPolling() {
      this.stopPolling()
      this.pollingInterval = setInterval(() => {
        this.fetchStatus().then((d) => {
          if (d.status === 'completed' || d.status === 'failed') {
            this.stopPolling()
          }
        })
      }, 3000)
    },
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval)
        this.pollingInterval = null
      }
    },
    reset() {
      this.stopPolling()
      this.jobId = null
      this.previewUrl = null
      this.duration = 0
      this.status = null
      this.progress = 0
      this.message = ''
      this.downloadUrl = null
      this.resultSizeMb = null
    },
  },
})

export default createPinia()
