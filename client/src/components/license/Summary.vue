<template>
  <div>
    <div class="text-h6 font-weight-medium">LICENSE</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">Here are your license details.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Resources</div>
    <v-text-field :loading="account.license === undefined" flat readonly solo v-model="resources" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Pricing</div>
    <v-text-field :loading="account.license === undefined" flat readonly solo v-model="pricing" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Next payment</div>
    <v-text-field :loading="account.license === undefined" flat readonly solo v-model="next" style="padding-top:5px" hide-details></v-text-field>
    <v-btn :disabled="account.license === undefined" color="info" @click="$router.push('/license/change')" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px;">Change license</v-btn>
  </div>
</template>

<style scoped>
::v-deep .v-input__control {
  border: 1px solid #b6b6b6 !important;
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
      if (this.account.license.resources == 1) return 'Free'
      return '$' + this.account.products.filter(x => x.resources == this.account.license.resources)[0]['price'] + ' / Month'
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
