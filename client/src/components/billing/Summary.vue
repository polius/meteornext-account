<template>
  <div>
    <div class="text-h6 font-weight-medium left" style="letter-spacing:1px!important; text-align:center">BILLING</div>
    <v-divider style="margin-top:15px; margin-bottom:20px"></v-divider>
    <div class="text-h6 font-weight-medium">Billing details</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Card</div>
    <v-text-field :loading="account.billing === undefined" flat readonly solo v-model="card" class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Last four digits</div>
    <v-text-field :loading="account.billing === undefined" flat readonly solo v-model="last4" class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Expiration date</div>
    <v-text-field :loading="account.billing === undefined" flat readonly solo v-model="expiration" class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <v-btn :disabled="account.billing === undefined" :loading="loading" color="#2196f3" @click="submitPaymentMethodChange" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px; margin-right:10px">{{ card == '-' ? 'Add payment method' : 'Update payment method' }}</v-btn>
    <v-btn :disabled="account.billing === undefined || account.billing.details.card === undefined" :loading="loading" color="#f18805" @click="dialog = true" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Remove payment method</v-btn>
    <v-dialog v-model="dialog" width="640px">
      <v-card>
        <v-toolbar dense flat color="rgb(50, 50, 60)" style="border:solid rgba(255, 255, 255, 0.12) 1px">
          <v-toolbar-title class="white--text text-body-1 font-weight-regular">Remove payment method</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:15px; background-color:rgb(65, 65, 75); border:solid rgba(255, 255, 255, 0.12) 1px; border-top:0px">
          <v-card style="background-color:rgb(60, 60, 70)">
            <v-row no-gutters align="center" justify="center">
              <v-col cols="auto" style="display:flex; margin:15px">
                <v-icon color="warning" size="20">fas fa-exclamation-triangle</v-icon>
              </v-col>
              <v-col>
                <div class="text-body-1" style="color:#e2e2e2">This action cannot be undone.</div>
              </v-col>
            </v-row>
          </v-card>
          <div class="text-body-1" style="margin-top:15px">Are you sure you want to remove the current payment method?</div>
          <v-divider style="margin-top:15px"></v-divider>
          <v-row no-gutters style="margin-top:15px;">
            <v-btn :loading="loading" color="primary" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitPaymentMethodRemove">Confirm</v-btn>
            <v-btn :disabled="loading" text color="white" @click="dialog = false" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
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
::v-deep .v-input--is-focused .v-input__control {
  border: 1px solid #2196f3 !important;
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
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    loading: false,
    dialog: false,
  }),
  props: {
    account: Object
  },
  computed: {
    card() {
      if (this.account.billing === undefined) return ''
      if (this.account.billing.details.card === undefined) return '-'
      return this.account.billing.details.card
    },
    last4() {
      if (this.account.billing === undefined) return ''
      if (this.account.billing.details.last4 === undefined) return '-'
      return this.account.billing.details.last4
    },
    expiration() {
      if (this.account.billing === undefined) return ''
      if (this.account.billing.details.expiration === undefined) return '-'
      return this.account.billing.details.expiration
    },
  },
  methods: {
    submitPaymentMethodChange() {
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
    },
    submitPaymentMethodRemove() {
      this.loading = true
      axios.delete('/billing/method')
        .then((response) => {
          EventBus.$emit('send-notification', response.data.message, '#20bf6b')
          EventBus.$emit('get-account')
          this.dialog = false
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
