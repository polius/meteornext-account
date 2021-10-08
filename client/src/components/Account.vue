<template>
  <div>
    <v-container style="max-width:100%">
      <div v-show="!$vuetify.breakpoint.smAndDown">
        <v-row no-gutters>
          <v-col cols="6" style="padding-right:6px">
            <Profile :loading="loading" :account="account" style="height:296px"/>
          </v-col>
          <v-col cols="6" style="padding-left:6px">
            <License :loading="loading" :account="account"/>
          </v-col>
        </v-row>
        <Billing style="margin-top:12px"/>
      </div>
      <div v-show="$vuetify.breakpoint.smAndDown">
        <Profile :loading="loading" :account="account"/>
        <License :loading="loading" :account="account" style="margin-top:12px"/>
        <Billing style="margin-top:12px"/>
      </div>
    </v-container>
  </div>
</template>

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
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("YYYY-MM-DD HH:mm:ss")
      return date
    },
  },
}
</script>