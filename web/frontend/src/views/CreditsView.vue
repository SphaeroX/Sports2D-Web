<template>
  <div class="credits">
    <h1>{{ $t('credits.title') }}</h1>
    <div class="card">
      <p>{{ $t('credits.text') }}</p>
      <ul>
        <li>
          <a href="https://github.com/davidpagnon/Sports2D" target="_blank" rel="noopener">{{ $t('credits.originalProject') }}</a>
          — David Pagnon
        </li>
        <li>
          <a href="https://github.com/perfanalytics/pose2sim" target="_blank" rel="noopener">{{ $t('credits.pose2sim') }}</a>
          — PerfAnalytics Lab
        </li>
      </ul>
      <p class="license">{{ $t('credits.license') }}</p>
    </div>
  </div>
</template>

<style scoped>
.credits { max-width: 700px; margin: 0 auto; }
.card {
  background: #1e293b; border: 1px solid #334155; border-radius: 12px;
  padding: 1.5rem; margin-top: 1rem; line-height: 1.6;
}
.card ul { margin: 1rem 0 1rem 1.2rem; }
.card li { margin-bottom: 0.5rem; }
.card a { color: #38bdf8; text-decoration: none; }
.license { font-size: 0.85rem; color: #64748b; margin-top: 1rem; }
</style>
