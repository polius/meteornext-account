<template>
  <div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Email</div>
    <v-text-field flat readonly solo v-model="email" :loading="loading" :disabled="loading" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Creation Date</div>
    <v-text-field flat readonly solo v-model="created_at" :loading="loading" :disabled="loading" style="padding-top:5px" hide-details></v-text-field>
  </div>
</template>

<style scoped>
::v-deep .v-input__control {
  border: 1px solid #d2ddec !important;
}
</style>

<script>
import moment from 'moment'

export default {
  data: () => ({
  }),
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
