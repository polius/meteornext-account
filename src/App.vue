<template>
  <v-app>
    <v-app-bar app color="#424242" dark>
      <v-img class="mr-2" :src="require('./assets/logo.png')" max-height="40" max-width="40" contain style="margin-bottom:2px"></v-img>
      <v-toolbar-title>Meteor Next | Account</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn class="d-none d-sm-flex">Logout</v-btn>
      <v-btn icon class="d-flex d-sm-none" title="Logout"><v-icon>fas fa-sign-out-alt</v-icon></v-btn>
    </v-app-bar>
    <v-main style="background-color:#303030">
      <Home/>
    </v-main>
  </v-app>
</template>

<style>
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

import Home from './components/Home';

export default {
  name: 'App',
  components: { Home },
  data: () => ({

  }),
}
</script>
