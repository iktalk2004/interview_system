<template>
  <div class="programmer-layout">
    <NavBar />
    <main class="main-content">
      <div class="content-wrapper">
        <slot></slot>
      </div>
    </main>
    <footer class="programmer-footer">
      <div class="footer-content">
        <div class="footer-terminal code-font">
          <span class="prompt-symbol">$</span>
          <span class="blink-cursor">&nbsp;</span>
        </div>
        <div class="footer-info">
          <span class="footer-text code-font">&lt;InterviewSystem/&gt;</span>
          <span class="footer-version">v1.0.0</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import NavBar from './NavBar.vue'
</script>

<style scoped>
.programmer-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.main-content {
  flex: 1;
  padding: 24px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
}

.programmer-footer {
  background: var(--code-bg);
  border-top: 1px solid var(--border-color);
  padding: 16px 24px;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-terminal {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--code-text);
}

.prompt-symbol {
  color: var(--accent-success);
  margin-right: 8px;
  font-weight: 600;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.footer-text {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 600;
}

.footer-version {
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-mono);
  padding: 4px 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .footer-content {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
