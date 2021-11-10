<template>
  <div>
    <v-toolbar color="#f5983b" style="max-height:64px">
      <v-img class="mr-2" :src="require('../assets/logo.png')" max-height="40" max-width="40" contain style="margin-bottom:2px"></v-img>
      <v-toolbar-title style="color:white">Meteor Next | Account</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="logout" class="d-none d-sm-flex" text style="color:white; height:45px"><v-icon size="22px" style="margin-right:10px">fas fa-sign-out-alt</v-icon>Logout</v-btn>
      <v-btn @click="logout" icon class="d-flex d-sm-none" title="Logout" style="color:white"><v-icon>fas fa-sign-out-alt</v-icon></v-btn>
    </v-toolbar>
    <v-container style="max-width:min(100%,90em)">
      <v-tabs v-model="tab" background-color="#fff3e0" slider-color="#fa8c1e" style="border-radius:3px;">
        <v-tab active-class="active" style="color:black">License</v-tab>
        <v-tab active-class="active" style="color:black">Billing</v-tab>
        <v-tab active-class="active" style="color:black">Profile</v-tab>
      </v-tabs>
      <License v-show="tab == 0" :loading="loading" :account="account"/>
      <Profile v-show="tab == 2" :loading="loading" :account="account"/>
    </v-container>
  </div>
</template>

<style scoped>
.active {
  color: #fa8c1e!important;
}
</style>

<script>
import EventBus from '../js/event-bus'
import axios from 'axios'
import moment from 'moment'

import Profile from './profile/Profile'
import License from './license/License'
import Billing from './billing/Billing'

export default {
  data: () => ({
    loading: false,
    account: {},
    tab: 0,
  }),
  components: { Profile, License, Billing },
  created() {
    this.getAccount()
  },
  mounted() {
    EventBus.$on('get-account', this.getAccount)
  },
  methods: {
    getAccount() {
      this.loading = true
      axios.get('/account')
        .then((response) => {
          this.account = response.data
          console.log(this.account)
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    logout() {
      this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
    },
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("YYYY-MM-DD HH:mm:ss")
      return date
    },
  },
}
</script>