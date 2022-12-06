<template>
  <div>
    <div class="text-h6 font-weight-medium left" style="letter-spacing:1px!important; text-align:center">LICENSE</div>
    <v-divider style="margin-top:15px; margin-bottom:20px"></v-divider>
    <div class="text-h6 font-weight-medium">License details</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Resources</div>
    <v-text-field :loading="account.license === undefined" flat readonly solo v-model="resources" class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Pricing</div>
    <v-text-field :loading="account.license === undefined" flat readonly solo v-model="pricing" class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Next payment</div>
    <v-text-field :loading="account.license === undefined" flat readonly solo v-model="next" class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <v-btn :disabled="account.license === undefined" color="info" @click="$router.push('/license/change')" style="font-size:0.95rem; letter-spacing:1px; font-weight:400; text-transform:none; color:white; margin-top:20px;">Change license</v-btn>
  </div>
</template>

<style scoped>
@media (max-width: 1040px) {
  .left {
    text-align:left !important;
  }
}
div {
  cursor:default !important;
}
::v-deep .v-input__control {
  border: 1px solid #b6b6b6 !important;
}
::v-deep .v-input__slot {
  background-color:rgba(61, 61, 80, 0.75) !important;
}
::v-deep .no-edit div div {
  cursor:default !important;
}
::v-deep .no-edit div div input {
  cursor:default !important;
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
    resources() {
      if (this.account.license === undefined) return ''
      if (this.account.license.resources == -1) return 'Unlimited'
      return this.account.license.resources + (this.account.license.resources == 1 ? ' Server' : ' Servers') + ' / User'
    },
    pricing() {
      if (this.account.license === undefined) return ''
      if (this.account.license.price == 0) return 'Free'
      return this.account.license.price + '€ / Month'
    },
    next() {
      if (this.account.license === undefined) return ''
      if (this.account.license.next === undefined) return '-'
      return this.dateFormat(this.account.license.next) + ' (' + this.diffFormat(this.account.license.next) + ')'
    },
  },
  methods: {
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("dddd, DD MMMM YYYY")
      return date
    },
    diffFormat(date) {
      if (date) {
        let days = moment(this.account.license.next).diff(moment(), 'days')
        if (days == 1) return '1 day'
        return days + ' days'
      }
    }
  }
}
</script>
