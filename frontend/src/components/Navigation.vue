<script setup lang="ts">
import { useTheme } from 'vuetify'
</script>

<template>
  <v-navigation-drawer rail permanent>
    <v-layout>
      <v-list density="compact" nav>
        <v-list-item value="account" :to="{ path: '/account' }">
            <v-icon small>mdi-account</v-icon>
        </v-list-item>
        <v-list-item value="transaction" :to="{ path: '/transaction' }">
            <v-icon small>mdi-send</v-icon>
        </v-list-item>
        <v-list-item value="admin" :to="{ path: '/admin' }">
            <v-icon small>mdi-security</v-icon>
        </v-list-item>
      </v-list>
    </v-layout>
  </v-navigation-drawer>
</template>