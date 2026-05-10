<template>
  <div class="video-editor">
    <div class="video-wrap">
      <video ref="video" :src="previewUrl" controls crossorigin="anonymous" @loadedmetadata="onLoaded" @timeupdate="onTimeUpdate"></video>
    </div>

    <p class="hint">{{ $t('home.editor.hint') }}</p>

    <div class="trim-controls">
      <div class="field">
        <label>{{ $t('home.editor.trimStart') }}</label>
        <input type="number" min="0" :max="duration" step="0.1" v-model.number="trimStart" />
      </div>
      <div class="field">
        <label>{{ $t('home.editor.trimEnd') }}</label>
        <input type="number" min="0" :max="duration" step="0.1" v-model.number="trimEnd" />
      </div>
      <div class="field actions">
        <button class="btn-small" @click="addSegment">{{ $t('home.editor.addSegment') }}</button>
        <button class="btn-small secondary" @click="resetTrim">{{ $t('home.editor.reset') }}</button>
      </div>
    </div>

    <div class="timeline-wrap" ref="timelineWrap">
      <canvas ref="canvas" :width="canvasWidth" height="60" @click="onCanvasClick"></canvas>
      <div class="time-labels">
        <span>0s</span>
        <span>{{ (duration/2).toFixed(1) }}s</span>
        <span>{{ duration.toFixed(1) }}s</span>
      </div>
    </div>

    <div v-if="segments.length" class="segments">
      <h4>Saved segments</h4>
      <div v-for="(seg, idx) in segments" :key="idx" class="segment-item">
        <span>{{ $t('home.editor.segmentLabel', { index: idx + 1 }) }}: {{ seg.start.toFixed(2) }}s - {{ seg.end.toFixed(2) }}s</span>
        <button class="btn-small danger" @click="removeSegment(idx)">{{ $t('home.editor.removeSegment') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  previewUrl: String,
  duration: { type: Number, default: 0 },
})
const emit = defineEmits(['update:segments'])

const segments = ref([])
const trimStart = ref(0)
const trimEnd = ref(0)
const canvasWidth = ref(800)
const video = ref(null)
const canvas = ref(null)
const timelineWrap = ref(null)

watch(segments, (v) => emit('update:segments', v), { deep: true })
watch(() => props.duration, (d) => { trimEnd.value = d })

function onLoaded() {
  if (props.duration) trimEnd.value = props.duration
  nextTick(drawTimeline)
}
function onTimeUpdate() {
  drawTimeline()
}

function drawTimeline() {
  if (!canvas.value || !props.duration) return
  const ctx = canvas.value.getContext('2d')
  const w = canvas.value.width
  const h = canvas.value.height
  ctx.clearRect(0, 0, w, h)

  // Background
  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, w, h)

  // Segments
  ctx.fillStyle = 'rgba(56, 189, 248, 0.3)'
  for (const seg of segments.value) {
    const x1 = (seg.start / props.duration) * w
    const x2 = (seg.end / props.duration) * w
    ctx.fillRect(x1, 0, x2 - x1, h)
  }

  // Trim range
  ctx.fillStyle = 'rgba(14, 165, 233, 0.5)'
  const tx1 = (trimStart.value / props.duration) * w
  const tx2 = (trimEnd.value / props.duration) * w
  ctx.fillRect(tx1, 0, tx2 - tx1, h)

  // Borders
  ctx.strokeStyle = '#334155'
  ctx.strokeRect(0, 0, w, h)

  // Current time
  if (video.value) {
    const ct = (video.value.currentTime / props.duration) * w
    ctx.strokeStyle = '#f87171'
    ctx.beginPath()
    ctx.moveTo(ct, 0)
    ctx.lineTo(ct, h)
    ctx.stroke()
  }

  // Handles
  ctx.fillStyle = '#0ea5e9'
  ctx.fillRect(tx1 - 3, 0, 6, h)
  ctx.fillRect(tx2 - 3, 0, 6, h)
}

watch([trimStart, trimEnd, segments], drawTimeline, { deep: true })

function onCanvasClick(e) {
  if (!canvas.value || !props.duration) return
  const rect = canvas.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const ratio = x / rect.width
  const time = Math.max(0, Math.min(props.duration, ratio * props.duration))

  // Snap to nearest 0.1s
  const snapped = Math.round(time * 10) / 10

  const distStart = Math.abs(snapped - trimStart.value)
  const distEnd = Math.abs(snapped - trimEnd.value)
  if (distStart < distEnd) {
    trimStart.value = Math.min(snapped, trimEnd.value - 0.5)
  } else {
    trimEnd.value = Math.max(snapped, trimStart.value + 0.5)
  }
}

function addSegment() {
  if (trimEnd.value <= trimStart.value) return
  segments.value.push({ start: trimStart.value, end: trimEnd.value })
}
function removeSegment(idx) {
  segments.value.splice(idx, 1)
}
function resetTrim() {
  trimStart.value = 0
  trimEnd.value = props.duration
}
</script>

<style scoped>
.video-editor { display: flex; flex-direction: column; gap: 1rem; }
.video-wrap video { width: 100%; max-height: 480px; border-radius: 8px; background: #000; }
.hint { font-size: 0.85rem; color: #94a3b8; }
.trim-controls { display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-end; }
.field { display: flex; flex-direction: column; gap: 0.3rem; }
.field label { font-size: 0.85rem; color: #cbd5e1; }
.field input {
  background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
  padding: 0.4rem 0.6rem; border-radius: 6px; width: 120px;
}
.actions { flex: 1; display: flex; flex-direction: row; gap: 0.5rem; justify-content: flex-end; }
.btn-small {
  background: #0ea5e9; color: #fff; border: none; padding: 0.4rem 0.8rem;
  border-radius: 6px; font-size: 0.85rem; cursor: pointer;
}
.btn-small.secondary { background: #334155; }
.btn-small.danger { background: #ef4444; }
.timeline-wrap { width: 100%; }
.timeline-wrap canvas { width: 100%; height: 60px; border-radius: 6px; cursor: pointer; background: #0f172a; border: 1px solid #334155; }
.time-labels { display: flex; justify-content: space-between; font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }
.segments { margin-top: 0.5rem; }
.segments h4 { font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.5rem; }
.segment-item {
  display: flex; justify-content: space-between; align-items: center;
  background: #0f172a; border: 1px solid #334155; border-radius: 6px;
  padding: 0.5rem 0.8rem; margin-bottom: 0.4rem; font-size: 0.9rem;
}
</style>
