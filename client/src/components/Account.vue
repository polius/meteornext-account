<template>
  <div style="height: calc(100% - 64px)">
    <v-toolbar color="rgba(50, 52, 69, 0.8)" style="max-height:64px; z-index:1">
      <v-img :src="require('../assets/logo.png')" max-height="40" max-width="40" contain style="margin-bottom:2px"></v-img>
      <v-toolbar-title style="color:white; margin-left:10px">Meteor Next | Account</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="logout" class="d-none d-sm-flex" text style="color:white; height:45px"><v-icon size="20" style="margin-right:10px">fas fa-sign-out-alt</v-icon>Logout</v-btn>
      <v-btn @click="logout" icon class="d-flex d-sm-none" title="Logout" style="color:white"><v-icon>fas fa-sign-out-alt</v-icon></v-btn>
    </v-toolbar>
    <v-container style="max-width:min(100%,65em); padding:0px">
      <v-tabs v-model="tab" background-color="transparent" center-active centered slider-color="white" height="55px">
        <v-tab class="tab" style="font-weight: 600; font-size:15px; color:white; background-color: rgba(61, 61, 80, 0.15);">License</v-tab>
        <v-tab class="tab" style="font-weight: 600; font-size:15px; color:white; background-color: rgba(61, 61, 80, 0.15);">Billing</v-tab>
        <v-tab class="tab" style="font-weight: 600; font-size:15px; color:white; background-color: rgba(61, 61, 80, 0.15);">Profile</v-tab>
      </v-tabs>
      <License v-show="tab == 0" :account="account" class="section" style="background-color:rgba(61, 61, 80, 0.75); border-radius:5px; padding:20px; margin-bottom:20px"/>
      <Billing v-show="tab == 1" :account="account" class="section" style="background-color:rgba(61, 61, 80, 0.75); border-radius:5px; padding:20px; margin-bottom:20px"/>
      <Profile v-show="tab == 2" :account="account" class="section" style="background-color:rgba(61, 61, 80, 0.75); border-radius:5px; padding:20px; margin-bottom:20px"/>
    </v-container>
  </div>
</template>

<style>
@media (max-width: 1040px) {
  .section {
    border-radius: 0px !important;
    margin-bottom: 0px !important;
  }
}
</style>

<script>
import EventBus from '../js/event-bus'
import axios from 'axios'

import Profile from './profile/Profile'
import License from './license/License'
import Billing from './billing/Billing'

export default {
  data: () => ({
    account: {},
    tab: 0,
  }),
  components: { Profile, License, Billing },
  beforeDestroy () {
    if (typeof window === 'undefined') return
  },
  created() {
    this.getAccount()
    if (this.$route.params.path !== undefined) {
      if (this.$route.params.path == 'billing') this.tab = 1
      else if (this.$route.params.path == 'profile') this.tab = 2
    }
  },
  mounted() {
    EventBus.$on('get-account', this.getAccount)
    if (this.$route.path == '/license') this.tab = 0
    else if (this.$route.path == '/billing') this.tab = 1
    else if (this.$route.path == '/profile') this.tab = 2
  },
  watch: {
    tab(value) {
      if (value == 0 && this.$route.path != '/license') this.$router.push('/license')
      else if (value == 1 && this.$route.path != '/billing') this.$router.push('/billing')
      else if (value == 2 && this.$route.path != '/profile') this.$router.push('/profile')
    }
  },
  methods: {
    getAccount() {
      axios.get('/account')
        .then((response) => {
          this.account = response.data
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
    },
    logout() {
      this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
    },
  },
}
</script>