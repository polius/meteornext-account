<template>
  <div style="margin:10px">
    <Summary :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Email :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Password :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <MFA :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Delete :account="account"/>
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
    account: Object
  },
  computed: {
    email() {
      return (this.account === undefined) ? '' : this.account.profile.email
    },
    created_at() {
      return (this.account === undefined) ? '' : this.dateFormat(this.account.profile.created_at)
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
