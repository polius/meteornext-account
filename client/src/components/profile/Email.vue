<template>
  <div>
    <div class="text-h6 font-weight-medium">Change email</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">We will email you a confirmation when changing your email, so please expect that email after submitting.</div>
    <v-form ref="form" @submit.prevent>
      <div class="text-body-2 font-weight-medium" style="margin-top:15px">New email</div>
      <v-text-field flat v-model="item" :readonly="loading" solo :rules="emailRules" style="padding-top:5px" hide-details v-on:keyup.enter="submitEmail()"></v-text-field>
    </v-form>
    <v-btn :loading="loading" color="info" @click="submitEmail" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Change email</v-btn>
  </div>
</template>

<style scoped>
::v-deep .v-input--is-focused .v-input__control {
  border: 1px solid #2196f3 !important; /* #005fcc */
}
::v-deep .v-input__control {
  border: 1px solid #b6b6b6 !important;
}
</style>

<script>
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    loading: false,
    item: '',
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(v) || 'E-mail must be valid',
    ],
  }),
  props: {
    email: String
  },
  methods: {
    submitEmail() {
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      // Check new email is different as current one
      this.loading = true
      const payload = { 'email': this.item }
      axios.post('/profile/email', payload)
        .then((response) => {
          this.item = ''
          EventBus.$emit('send-notification', response.data.message, '#20bf6b')
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