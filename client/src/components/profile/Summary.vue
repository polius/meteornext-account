<template>
  <div>
    <div class="text-h6 font-weight-medium" style="letter-spacing:1px!important">PROFILE</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">Here are your profile details.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Name</div>
    <v-text-field :loading="account.profile === undefined" flat readonly solo v-model="name" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Email</div>
    <v-text-field :loading="account.profile === undefined" flat readonly solo v-model="email" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Creation date</div>
    <v-text-field :loading="account.profile === undefined" flat readonly solo v-model="created" style="padding-top:5px" hide-details></v-text-field>
  </div>
</template>

<style scoped>
::v-deep .v-input__control {
  border: 1px solid #b6b6b6 !important;
}
::v-deep .v-input__slot {
  background-color:rgba(61, 61, 80, 0.75) !important;
}
</style>

<script>
import moment from 'moment'

export default {
  data: () => ({
  }),
  props: {
    account: Object
  },
  computed: {
    name() {
      return (this.account.profile === undefined) ? '' : this.account.profile.name
    },
    email() {
      return (this.account.profile === undefined) ? '' : this.account.profile.email
    },
    created() {
      return (this.account.profile === undefined) ? '' : this.dateFormat(this.account.profile.created_date)
    },
  },
  methods: {
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("DD MMMM, YYYY")
      return date
    },
  }
}
</script>
