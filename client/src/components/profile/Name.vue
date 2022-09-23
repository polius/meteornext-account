<template>
  <div>
    <div class="text-h6 font-weight-medium">Change name</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">We will use this name for when we send you emails. Should be the customer's full name or business name.</div>
    <v-form ref="form" @submit.prevent>
      <div class="text-body-2 font-weight-medium" style="margin-top:15px">New name</div>
      <v-text-field flat v-model="item" :readonly="loading" solo style="padding-top:5px" hide-details v-on:keyup.enter="submitName()"></v-text-field>
    </v-form>
    <v-btn :loading="loading" color="info" @click="submitName" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Change name</v-btn>
  </div>
</template>

<style scoped>
::v-deep .v-input--is-focused .v-input__control {
  border: 1px solid #2196f3 !important;
}
::v-deep .v-input__control {
  border: 1px solid #b6b6b6 !important;
}
::v-deep .v-input__slot {
  background-color:rgba(61, 61, 80, 0.75) !important;
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
    name: String
  },
  methods: {
    submitName() {
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = { 'name': this.item }
      axios.post('/profile/name', payload)
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