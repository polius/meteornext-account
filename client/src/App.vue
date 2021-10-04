<template>
  <v-app>
    <v-toolbar v-if="isLoggedIn" color="#424242" style="max-height:64px">
      <v-img class="mr-2" :src="require('./assets/logo.png')" max-height="40" max-width="40" contain style="margin-bottom:2px"></v-img>
      <v-toolbar-title>Meteor Next | Account</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="logout" class="d-none d-sm-flex">Logout</v-btn>
      <v-btn @click="logout" icon class="d-flex d-sm-none" title="Logout"><v-icon>fas fa-sign-out-alt</v-icon></v-btn>
    </v-toolbar>
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

<style>
body {
  background-color:#303030;
}
/* Dark Scrollbar */
.dark_scrollbar::-webkit-scrollbar {
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
}
</style>

<script>
// Scrollbar - Firefox
document.documentElement.style.setProperty('scrollbar-color', '#303030 #424242');
// Scrollbar - Chrome
document.documentElement.classList.add("dark_scrollbar");

export default {
  data: () => ({
    // Snackbar
    snackbar: false,
    snackbarTimeout: Number(3000),
    snackbarText: '',
    snackbarColor: ''
  }),
  computed: {
    isLoggedIn: function() { return this.$store.getters['app/isLoggedIn'] },
  },
  methods: {
    logout() {
      this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
    },
  }
}
</script>
