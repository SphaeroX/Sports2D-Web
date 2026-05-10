import { createPinia } from 'pinia'
import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = ''
const USER_ID_KEY = 'sports2d_user_id'
const JOBS_HISTORY_KEY = 'sports2d_jobs_history'

function getUserId() {
  return localStorage.getItem(USER_ID_KEY)
}

function loadJobHistory() {
  try {
    return JSON.parse(localStorage.getItem(JOBS_HISTORY_KEY) || '[]')
  } catch {
    return []
  }
}

function saveJobHistory(jobs) {
  localStorage.setItem(JOBS_HISTORY_KEY, JSON.stringify(jobs))
}

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
    jobHistory: loadJobHistory(),
    historyPollingInterval: null,
  }),
  getters: {
    activeJobs() {
      return this.jobHistory.filter(j => ['pending','preprocessing','queued','processing'].includes(j.status))
    },
    completedJobs() {
      return this.jobHistory.filter(j => j.status === 'completed')
    },
    failedJobs() {
      return this.jobHistory.filter(j => j.status === 'failed')
    },
  },
  actions: {
    async uploadVideo(file) {
      const form = new FormData()
      form.append('file', file)
      const userId = getUserId()
      if (userId) {
        form.append('user_id', userId)
      }
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
      const userId = getUserId()
      const res = await axios.post(`${API_BASE}/api/jobs/process`, {
        job_id: this.jobId,
        user_id: userId,
        segments,
        params,
        expert_mode: expertMode,
      })
      this.status = 'queued'
      // Add to history
      const history = loadJobHistory()
      if (!history.find(j => j.job_id === this.jobId)) {
        history.unshift({
          job_id: this.jobId,
          status: 'queued',
          created_at: new Date().toISOString(),
          progress_percent: 0,
          message: '',
          download_url: null,
          result_size_mb: null,
          original_filename: null,
        })
        saveJobHistory(history)
        this.jobHistory = history
      }
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
    async fetchJobHistory() {
      const userId = getUserId()
      if (!userId) return
      try {
        const res = await axios.get(`${API_BASE}/api/jobs/list`, { params: { user_id: userId } })
        const jobs = res.data.jobs || []
        // Merge with local history to preserve any local metadata
        const localHistory = loadJobHistory()
        const merged = jobs.map(job => {
          const local = localHistory.find(j => j.job_id === job.job_id)
          return { ...local, ...job }
        })
        saveJobHistory(merged)
        this.jobHistory = merged
      } catch (err) {
        console.error('Failed to fetch job history', err)
      }
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
    startHistoryPolling() {
      this.stopHistoryPolling()
      this.fetchJobHistory()
      this.historyPollingInterval = setInterval(() => {
        this.fetchJobHistory()
      }, 5000)
    },
    stopHistoryPolling() {
      if (this.historyPollingInterval) {
        clearInterval(this.historyPollingInterval)
        this.historyPollingInterval = null
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
