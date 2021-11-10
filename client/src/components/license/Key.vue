<template>
  <div>
    <div class="text-h6 font-weight-medium">License key</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:10px">Use the following credentials to register your copy of Meteor Next.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Email</div>
    <v-text-field flat @click="$event.target.select()" solo v-model="email" readonly label="Email" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Key</div>
    <v-text-field flat @click="$event.target.select()" solo v-model="key" readonly label="Key" style="padding-top:5px" hide-details></v-text-field>
    <div class="body-1" style="margin-top:15px; margin-bottom:15px"><v-icon :style="`font-size:16px; margin-right:10px; margin-bottom:5px; color:${in_use ? '#00b16a' : '#00b16a'}`">{{ in_use ? 'fas fa-lock' : 'fas fa-unlock' }}</v-icon>{{ in_use ? 'License registered' : 'License ready to be registered' }}</div>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <div class="text-h6 font-weight-medium">Unregister license</div>
    <div class="text-body-1 font-weight-light" style="margin-top:15px">A license key can be used only in one device. To be able to use it in another device, first you have to unregister it.</div>
    <v-btn @click="submitUnregister" color="#2c7be5" title="Unregister your existing license to use it in another computer" style="font-size:0.9375rem; font-weight:400; text-transform:none; color:white; margin-top:15px" :disabled="!in_use" :loading="loading">Unregister license</v-btn>
  </div>
</template>

<style scoped>
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
    account: Object
  },
  computed: {
    dialog: {
      get() { return this.enabled },
      set(value) { this.$emit('update', value) },
    },
    email() {
      if (this.loading || this.account === undefined || this.account.profile === undefined) return ''
      else return this.account.profile.email
    },
    key() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.key
    },
    in_use() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.in_use
    }
  },
  methods: {
    submitUnregister() {
      // this.loading = true
      axios.post('/account/unregister')
        .then((response) => {
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