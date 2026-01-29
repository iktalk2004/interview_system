<template>
  <div id="app">
    <NavBar/>
    <router-view/>
  </div>
</template>

<script setup>
import NavBar from '@/components/NavBar.vue';
</script>

<style>#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}
</style>