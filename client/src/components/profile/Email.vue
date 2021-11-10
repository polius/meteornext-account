<template>
  <div>
    <div class="text-h6 font-weight-medium">Change email</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">We will email you a confirmation when changing your email, so please expect that email after submitting.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">New email</div>
    <v-text-field flat v-model="item" :readonly="loading" solo style="padding-top:5px" hide-details></v-text-field>
    <v-btn :loading="loading" color="#2c7be5" @click="submitEmail" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Update email</v-btn>
  </div>
</template>

<style scoped>
::v-deep .v-input--is-focused .v-input__control {
  border: 1px solid #2c7be5 !important; /* #005fcc */
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
    item: '',
  }),
  props: {
    enabled: Boolean,
    email: String
  },
  computed: {
    validEmail() {
      let valid = !!this.item && /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(this.item)
      return valid
    }
  },
  methods: {
    submitEmail() {
      this.loading = true
      const payload = { 'email': this.item }
      axios.put('/account/email', payload)
        .then((response) => {
          this.dialog = false
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
          EventBus.$emit('get-account')
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
  },
}
</script>