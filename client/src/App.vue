<template>
  <v-app>
    <v-main style="background-color:#fffcfa">
      <router-view/>
    </v-main>
    <v-snackbar v-model="snackbar" :multi-line="false" :timeout="snackbarTimeout" :color="snackbarColor" top style="padding-top:0px;">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<style>
body {
  background-color:#fffcfa;
}
</style>

<script>
import EventBus from './js/event-bus'

export default {
  data: () => ({
    // Snackbar
    snackbar: false,
    snackbarTimeout: Number(3000),
    snackbarText: '',
    snackbarColor: '',
  }),
  mounted() {
    EventBus.$on('send-notification', this.notification)
  },
  methods: {
    notification(message, color) {
      this.snackbarText = message
      this.snackbarColor = color
      this.snackbar = true
    },
  }
}
</script>
