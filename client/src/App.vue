<template>
  <v-app>
    <v-main>
      <router-view/>
    </v-main>
    <v-footer padless>
      <div style="margin-left:auto; margin-right:auto; margin-top:15px; margin-bottom:15px">
        <a href="https://www.meteornext.io/terms-of-service" target="_blank" style="text-decoration:none; color:white; padding:15px">Terms of Service</a>
        <span>|</span>
        <a href="https://www.meteornext.io/privacy" target="_blank" style="text-decoration:none; color:white; padding:15px">Privacy</a>
        <span>|</span>
        <a href="https://www.meteornext.io/cookies" target="_blank" style="text-decoration:none; color:white; padding:15px">Cookies</a>
      </div>
      <div style="width:100%; color:white; text-align: center; font-size:14px; padding-bottom:15px">Copyright © {{ new Date().getFullYear() }} Meteor Next</div>
    </v-footer>
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
