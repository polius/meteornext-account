<template>
  <div>
    <v-container style="max-width:100%">
      <div v-show="!$vuetify.breakpoint.smAndDown">
        <v-row no-gutters>
          <v-col cols="6" style="padding-right:6px">
            <Profile style="height:296px"/>
          </v-col>
          <v-col cols="6" style="padding-left:6px">
            <License/>
          </v-col>
        </v-row>
        <Billing style="margin-top:12px"/>
      </div>
      <div v-show="$vuetify.breakpoint.smAndDown">
        <Profile/>
        <License style="margin-top:12px"/>
        <Billing style="margin-top:12px"/>
      </div>
    </v-container>
    <v-snackbar v-model="snackbar" :multi-line="false" :timeout="snackbarTimeout" :color="snackbarColor" top style="padding-top:0px;">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import axios from 'axios'
import moment from 'moment'

import Profile from './account/Profile'
import License from './account/License'
import Billing from './account/Billing'

export default {
  data: () => ({
    loading: false,
    account: {},
    // Snackbar
    snackbar: false,
    snackbarTimeout: Number(3000),
    snackbarText: '',
    snackbarColor: ''
  }),
  components: { Profile, License, Billing },
  created() {
    this.getAccount()
  },
  methods: {
    getAccount() {
      axios.get('/account')
        .then((response) => {
          this.account = response.data
          console.log(this.account)
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else this.notification(error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("YYYY-MM-DD HH:mm:ss")
      return date
    },
    notification(message, color) {
      this.snackbarText = message
      this.snackbarColor = color 
      this.snackbar = true
    }
  },
}
</script>