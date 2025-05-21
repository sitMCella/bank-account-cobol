<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
</script>

<template>
  <v-app-bar :elevation="2">
    <template v-slot:prepend>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>
    </template>
    <v-app-bar-title>Bank Account</v-app-bar-title>
  </v-app-bar>
</template>