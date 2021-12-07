<template>
  <div style="height: calc(100% - 64px)">
    <v-toolbar color="#424242" style="max-height:64px; z-index:1">
      <v-img class="mr-2" :src="require('../assets/logo.png')" max-height="40" max-width="40" contain style="margin-bottom:2px"></v-img>
      <v-toolbar-title style="color:white">Meteor Next | Account</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="logout" class="d-none d-sm-flex" text style="color:white; height:45px"><v-icon size="20" style="margin-right:10px">fas fa-sign-out-alt</v-icon>Logout</v-btn>
      <v-btn @click="logout" icon class="d-flex d-sm-none" title="Logout" style="color:white"><v-icon>fas fa-sign-out-alt</v-icon></v-btn>
    </v-toolbar>
    <div :style="{ height:'100%', width:'100%', padding:'0px', backgroundImage: 'url(' + require('@/assets/bg.jpg') + ')', backgroundRepeat: 'no-repeat', backgroundSize: 'cover' }">
      <v-container style="max-width:min(100%,65em); background-color:#444444; padding:0px">
        <v-tabs v-model="tab" background-color="#333333" center-active centered slider-color="white" height="55px">
          <v-tab active-class="active" style="color:white">License</v-tab>
          <v-tab active-class="active" style="color:white">Billing</v-tab>
          <v-tab active-class="active" style="color:white">Profile</v-tab>
        </v-tabs>
        <License v-show="tab == 0" :account="account" :style="`padding:15px 20px 25px; margin-bottom:${isMobile ? '0px' : '20px'}`"/>
        <Billing v-show="tab == 1" :account="account" :style="`padding:15px 20px 25px; margin-bottom:${isMobile ? '0px' : '20px'}`"/>
        <Profile v-show="tab == 2" :account="account" :style="`padding:15px 20px 25px; margin-bottom:${isMobile ? '0px' : '20px'}`"/>
      </v-container>
    </div>
  </div>
</template>

<style scoped>
.active {
  color: white!important;
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
    isMobile: false,
  }),
  components: { Profile, License, Billing },
  beforeDestroy () {
    if (typeof window === 'undefined') return
    window.removeEventListener('resize', this.onResize, { passive: true })
  },
  created() {
    this.onResize()
    this.getAccount()
    if (this.$route.params.path !== undefined) {
      if (this.$route.params.path == 'billing') this.tab = 1
      else if (this.$route.params.path == 'profile') this.tab = 2
    }
  },
  mounted() {
    window.addEventListener('resize', this.onResize, { passive: true })
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
    onResize () {
      this.isMobile = window.innerWidth < 1040
    },
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