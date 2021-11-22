<template>
  <div>
    <div class="text-h6 font-weight-medium">LICENSE</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">Here are your license details.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Resources</div>
    <v-text-field flat readonly solo v-model="resources" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Pricing</div>
    <v-text-field flat readonly solo v-model="pricing" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Expiration Date</div>
    <v-text-field flat readonly solo v-model="expiration" style="padding-top:5px" hide-details></v-text-field>
  </div>
</template>

<style scoped>
::v-deep .v-input__control {
  border: 1px solid #d2ddec !important;
}
</style>

<script>
export default {
  name: 'Summary',
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
    expiration() {
      if (this.account.license === undefined) return ''
      if (this.account.license.expiration) return this.account.license.expiration_date
      return 'Lifetime'
    },
  },
}
</script>
