<template>
  <div style="margin:10px">
    <Summary :loading="loading" :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Email :loading="loading" :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Password :loading="loading" :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <MFA :loading="loading" :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Delete :loading="loading" :account="account"/>
  </div>
</template>

<script>
import moment from 'moment'

import Summary from './Summary'
import Password from './Password'
import Email from './Email'
import MFA from './MFA'
import Delete from './Delete'

export default {
  data: () => ({
  }),
  components: { Summary, Password, Email, MFA, Delete },
  props: {
    loading: Boolean,
    account: Object
  },
  computed: {
    email() {
      return (this.loading || this.account === undefined) ? '' : this.account.profile.email
    },
    created_at() {
      return (this.loading || this.account === undefined) ? '' : this.dateFormat(this.account.profile.created_at)
    },
  },
  methods: {
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("YYYY-MM-DD HH:mm:ss")
      return date
    },
  }
}
</script>
