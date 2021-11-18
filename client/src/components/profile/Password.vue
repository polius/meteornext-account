<template>
  <div>
      <div class="text-h6 font-weight-medium">Change password</div>
      <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">To create a new password, you have to meet all of the following requirements:</div>
      <v-card elevation="1">
        <v-card-text style="padding:10px 26px">
          <li class="text-body-2">Minimum 8 characters</li>
          <li class="text-body-2">At least one letter</li>
          <li class="text-body-2">At least one number</li>
          <li class="text-body-2">Cannot be the same as the previous password</li>
        </v-card-text>
      </v-card>
      <v-form ref="passwordForm" @submit.prevent>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">Current password</div>
        <v-text-field flat v-model="item.current" :readonly="loading" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">New password</div>
        <v-text-field flat v-model="item.new" :readonly="loading" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">Confirm new password</div>
        <v-text-field flat v-model="item.repeat" :readonly="loading" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
      </v-form>
      <v-btn :loading="loading" color="#2c7be5" @click="submitPassword" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Update password</v-btn>
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
    item: { current: '', new: '', repeat: '' }
  }),
  props: {
    enabled: Boolean
  },
  computed: {
    dialog: {
      get() { return this.enabled },
      set(value) { this.$emit('update', value) },
    }
  },
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
          this.dialog = false
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