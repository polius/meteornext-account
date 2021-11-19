<template>
  <div>
      <div class="text-h6 font-weight-medium">Change password</div>
      <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">The new password has to meet the following requirements: Minimum 8 characters, at least one letter and at least one number.</div>
      <v-form ref="passwordForm" @submit.prevent>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">Current password</div>
        <v-text-field flat v-model="item.current" :readonly="loading" type="password" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">New password</div>
        <v-text-field flat v-model="item.new" :readonly="loading" type="password" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">Confirm new password</div>
        <v-text-field flat v-model="item.repeat" :readonly="loading" type="password" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
      </v-form>
      <v-btn :loading="loading" color="#2196f3" @click="submitPassword" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Change password</v-btn>
  </div>
</template>

<style scoped>
::v-deep .v-input--is-focused .v-input__control {
  border: 1px solid #2196f3 !important; /* #005fcc */
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
    item: { current: '', new: '', repeat: '' },
  }),
  methods: {
    submitPassword() {
      // Check if all fields are filled
      if (!this.$refs.passwordForm.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = this.item
      axios.put('/account/password', payload)
        .then((response) => {
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
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