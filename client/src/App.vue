<template>
  <v-app>
    <v-main>
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

<style src="@/fonts/roboto.css"></style>
<style src="@/fonts/materialicons.css"></style>

<style>
#app {
  height: 100%;
  padding: 0px;
  background-color: transparent;
  background-image: url('https://www.meteornext.io/assets/bg.png');
  background-repeat: no-repeat;
  background-size: cover;
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
