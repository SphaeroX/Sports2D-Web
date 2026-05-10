<template>
  <div class="app">
    <nav class="navbar">
      <div class="brand">
        <router-link to="/" class="logo">Sports2D Web</router-link>
      </div>
      <div class="links">
        <router-link to="/">{{ $t('nav.home') }}</router-link>
        <router-link to="/credits">{{ $t('nav.credits') }}</router-link>
        <select v-model="$i18n.locale" class="lang-select">
          <option value="en">English</option>
          <option value="de">Deutsch</option>
        </select>
      </div>
    </nav>
    <main>
      <router-view />
    </main>
    <footer class="footer">
      <p>
        Powered by
        <a href="https://github.com/davidpagnon/Sports2D" target="_blank" rel="noopener">Sports2D</a>
        &amp;
        <a href="https://github.com/perfanalytics/pose2sim" target="_blank" rel="noopener">Pose2Sim</a>
      </p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; }
.navbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 2rem; background: #1e293b; border-bottom: 1px solid #334155;
}
.brand .logo { color: #38bdf8; font-size: 1.4rem; font-weight: 700; text-decoration: none; }
.links { display: flex; align-items: center; gap: 1.5rem; }
.links a { color: #cbd5e1; text-decoration: none; font-size: 0.95rem; }
.links a:hover { color: #38bdf8; }
.lang-select {
  background: #0f172a; color: #e2e8f0; border: 1px solid #334155;
  border-radius: 6px; padding: 0.3rem 0.6rem; font-size: 0.9rem;
}
main { flex: 1; padding: 2rem; max-width: 1100px; margin: 0 auto; width: 100%; }
.footer {
  text-align: center; padding: 1rem; background: #1e293b;
  border-top: 1px solid #334155; font-size: 0.85rem; color: #94a3b8;
}
.footer a { color: #38bdf8; text-decoration: none; }
</style>
