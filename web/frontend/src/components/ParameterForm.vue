<template>
  <div class="param-form">
    <div class="mode-toggle">
      <label>{{ $t('home.parameters.mode.label') }}</label>
      <div class="toggle">
        <button :class="{ active: !expertMode }" @click="expertMode = false">{{ $t('home.parameters.mode.standard') }}</button>
        <button :class="{ active: expertMode }" @click="expertMode = true">{{ $t('home.parameters.mode.expert') }}</button>
      </div>
    </div>

    <div class="grid">
      <!-- Standard fields -->
      <div class="field">
        <label>{{ $t('home.parameters.personHeight') }}</label>
        <input type="number" step="0.01" v-model.number="params.first_person_height" />
      </div>

      <div class="field">
        <label>{{ $t('home.parameters.personsToDetect') }}</label>
        <select v-model="params.nb_persons_to_detect">
          <option value="all">{{ $t('home.parameters.all') }}</option>
          <option :value="1">1</option>
          <option :value="2">2</option>
          <option :value="3">3</option>
        </select>
      </div>

      <div class="field">
        <label>{{ $t('home.parameters.poseModel') }}</label>
        <select v-model="params.pose_model">
          <option>Body_with_feet</option>
          <option>Whole_body</option>
          <option>Body</option>
          <option>Lower_body</option>
        </select>
      </div>

      <div class="field">
        <label>{{ $t('home.parameters.device') }}</label>
        <select v-model="params.device">
          <option value="auto">Auto</option>
          <option value="CPU">CPU</option>
          <option value="CUDA">CUDA</option>
        </select>
      </div>

      <div class="field">
        <label>{{ $t('home.parameters.trackingMode') }}</label>
        <select v-model="params.tracking_mode">
          <option>sports2d</option>
          <option>deepsort</option>
        </select>
      </div>

      <!-- Expert fields -->
      <template v-if="expertMode">
        <div class="field">
          <label class="with-tip">
            {{ $t('home.parameters.detFrequency') }}
            <span class="tip" :title="$t('home.parameters.tooltip.detFrequency')">?</span>
          </label>
          <input type="number" min="1" v-model.number="params.det_frequency" />
        </div>

        <div class="field">
          <label class="with-tip">
            {{ $t('home.parameters.doIK') }}
            <span class="tip" :title="$t('home.parameters.tooltip.doIK')">?</span>
          </label>
          <select v-model="params.do_ik">
            <option :value="true">On</option>
            <option :value="false">Off</option>
          </select>
        </div>

        <div class="field">
          <label class="with-tip">
            {{ $t('home.parameters.filterType') }}
            <span class="tip" :title="$t('home.parameters.tooltip.filterType')">?</span>
          </label>
          <select v-model="params.filter_type">
            <option>butterworth</option>
            <option>kalman</option>
            <option>one_euro</option>
            <option>gcv_spline</option>
            <option>acc_minimizing</option>
          </select>
        </div>

        <div class="field" v-if="params.filter_type === 'butterworth'">
          <label class="with-tip">
            {{ $t('home.parameters.cutoffFreq') }}
            <span class="tip" :title="$t('home.parameters.tooltip.cutoffFreq')">?</span>
          </label>
          <input type="number" step="0.5" v-model.number="params.butterworth_cut_off_frequency" />
        </div>

        <div class="field">
          <label>{{ $t('home.parameters.jointAngles') }}</label>
          <div class="checkboxes">
            <label v-for="angle in allJointAngles" :key="angle">
              <input type="checkbox" :value="angle" v-model="params.joint_angles" />
              {{ angle }}
            </label>
          </div>
        </div>

        <div class="field">
          <label>{{ $t('home.parameters.segmentAngles') }}</label>
          <div class="checkboxes">
            <label v-for="angle in allSegmentAngles" :key="angle">
              <input type="checkbox" :value="angle" v-model="params.segment_angles" />
              {{ angle }}
            </label>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  params: { type: Object, default: () => ({}) },
  expertMode: { type: Boolean, default: false },
})
const emit = defineEmits(['update:params', 'update:expertMode'])

const expertMode = ref(props.expertMode)
watch(expertMode, (v) => emit('update:expertMode', v))

const defaults = {
  first_person_height: 1.65,
  nb_persons_to_detect: 'all',
  pose_model: 'Body_with_feet',
  device: 'auto',
  tracking_mode: 'sports2d',
  det_frequency: 4,
  do_ik: false,
  filter_type: 'butterworth',
  butterworth_cut_off_frequency: 6.0,
  butterworth_order: 4,
  joint_angles: [
    'Right ankle','Left ankle','Right knee','Left knee','Right hip','Left hip',
    'Right shoulder','Left shoulder','Right elbow','Left elbow','Right wrist','Left wrist'
  ],
  segment_angles: [
    'Right foot','Left foot','Right shank','Left shank','Right thigh','Left thigh',
    'Pelvis','Trunk','Shoulders','Head','Right arm','Left arm','Right forearm','Left forearm'
  ],
  correct_segment_angles_with_floor_angle: true,
}

const params = ref({ ...defaults, ...props.params })
watch(params, (v) => emit('update:params', v), { deep: true })

const allJointAngles = [
  'Right ankle','Left ankle','Right knee','Left knee','Right hip','Left hip',
  'Right shoulder','Left shoulder','Right elbow','Left elbow','Right wrist','Left wrist'
]
const allSegmentAngles = [
  'Right foot','Left foot','Right shank','Left shank','Right thigh','Left thigh',
  'Pelvis','Trunk','Shoulders','Head','Right arm','Left arm','Right forearm','Left forearm'
]
</script>

<style scoped>
.param-form { display: flex; flex-direction: column; gap: 1.2rem; }
.mode-toggle { display: flex; align-items: center; gap: 1rem; }
.mode-toggle label { font-weight: 600; }
.toggle { display: inline-flex; border-radius: 8px; overflow: hidden; border: 1px solid #334155; }
.toggle button {
  background: #0f172a; color: #94a3b8; border: none; padding: 0.5rem 1rem; cursor: pointer; font-size: 0.9rem;
}
.toggle button.active { background: #0ea5e9; color: #fff; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field label { font-size: 0.85rem; color: #cbd5e1; }
.field input, .field select {
  background: #0f172a; border: 1px solid #334155; color: #e2e8f0;
  padding: 0.45rem 0.6rem; border-radius: 6px; font-size: 0.9rem;
}
.with-tip { display: flex; align-items: center; gap: 0.4rem; }
.tip {
  display: inline-flex; align-items: center; justify-content: center;
  width: 16px; height: 16px; border-radius: 50%; background: #334155;
  color: #94a3b8; font-size: 0.7rem; cursor: help;
}
.checkboxes { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; }
.checkboxes label { display: flex; align-items: center; gap: 0.3rem; font-size: 0.85rem; color: #cbd5e1; cursor: pointer; }
.checkboxes input { accent-color: #0ea5e9; }
</style>
