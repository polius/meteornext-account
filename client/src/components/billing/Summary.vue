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
    <v-btn :loading="loading" color="#2196f3" @click="submitChange" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Change payment method</v-btn>
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
export default {
  data: () => ({
    card: 'VISA',
    last4: '4242',
    expiration: '08/2022',
    loading: false,
  }),
  props: {
    account: Object
  },
  methods: {
    submitChange() {
      
    }
  }
}
</script>
