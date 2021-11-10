<template>
  <v-app>
    <v-main style="background-color:#f6f7ff">
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
  background-color:#f6f7ff;
}
/* Dark Scrollbar */
/* .dark_scrollbar::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 15px;
  background-color: #424242;
}
.dark_scrollbar::-webkit-scrollbar-track {
  background: #424242;
}
.dark_scrollbar::-webkit-scrollbar-thumb {
  min-height: 25px;
  background: #303030;
  border: 3px solid transparent;
  border-radius: 10px;
  background-clip: content-box;
}
.dark_scrollbar::-webkit-scrollbar-corner {
  background: #303030;
}
::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 15px;
  background-color: #424242;
}
::-webkit-scrollbar-track {
  background: #424242;
}
::-webkit-scrollbar-thumb {
  min-height: 25px;
  background:  #303030;
  border: 3px solid transparent;
  border-radius: 10px;
  background-clip: content-box;
}
::-webkit-scrollbar-corner {
  background: #303030 ;
} */
</style>

<script>
import EventBus from './js/event-bus'

// Scrollbar - Firefox
// document.documentElement.style.setProperty('scrollbar-color', '#303030 #424242');
// Scrollbar - Chrome
// document.documentElement.classList.add("dark_scrollbar");

export default {
  data: () => ({
    // Snackbar
    snackbar: false,
    snackbarTimeout: Number(3000),
    snackbarText: '',
    snackbarColor: ''
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
