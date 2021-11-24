<template>
  <div>
    <div class="text-h6 font-weight-medium">BILLING</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">Here are your billing details.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Card</div>
    <v-text-field flat readonly solo v-model="card" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Last Four Digits</div>
    <v-text-field flat readonly solo v-model="last4" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Expiration Date</div>
    <v-text-field flat readonly solo v-model="expiration" style="padding-top:5px" hide-details></v-text-field>
    <v-btn :loading="loading" color="#2196f3" @click="submitPaymentMethod" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">{{ card == '-' ? 'Add payment method' : 'Change payment method' }}</v-btn>
  </div>
</template>

<style scoped>
::v-deep .v-input--is-focused .v-input__control {
  border: 1px solid #2196f3 !important;
}
::v-deep .v-input__control {
  border: 1px solid #d2ddec !important;
}
</style>

<script>
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    loading: false,
  }),
  props: {
    account: Object
  },
  computed: {
    card() {
      if (this.account.billing === undefined || this.account.billing.details.card === undefined) return '-'
      else return this.account.billing.details.card
    },
    last4() {
      if (this.account.billing === undefined ||  this.account.billing.details.last4 === undefined) return '-'
      else return this.account.billing.details.last4
    },
    expiration() {
      if (this.account.billing === undefined ||  this.account.billing.details.expiration === undefined) return '-'
      else return this.account.billing.details.expiration
    },
  },
  methods: {
    submitPaymentMethod() {
      this.loading = true
      axios.post('/billing/method')
        .then((response) => {
          window.location.href = response.data.url
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    }
  }
}
</script>
