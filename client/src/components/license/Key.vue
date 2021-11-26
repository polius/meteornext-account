<template>
  <div>
    <div class="text-h6 font-weight-medium">License key</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:10px">Use the following credentials to register your copy of Meteor Next.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Access Key</div>
    <v-text-field flat @click="$event.target.select()" solo v-model="access_key" readonly style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Secret Key</div>
    <v-text-field flat @focus="showSecretKey = true" @blur="showSecretKey = false" @click="$event.target.select()" solo v-model="secret_key" readonly :type="showSecretKey ? 'text' : 'password'" style="padding-top:5px" hide-details></v-text-field>
    <div v-if="in_use != null" class="body-1" style="margin-top:15px; margin-bottom:15px"><v-icon :style="`font-size:16px; margin-right:10px; margin-bottom:3px; color:${in_use ? '#ff944d' : '#20bf6b'}`">fas fa-circle</v-icon>{{ in_use ? 'License in use.' : 'License ready to be registered.' }}</div>
    <div v-if="in_use" class="text-body-1 font-weight-light">A license key can be used only in one device. To be able to use it in another device, first you have to unregister it from the first one.</div>
    <v-btn v-if="in_use" @click="dialog = true" color="#fb8c00" title="Unregister your existing license to use it in another computer" style="font-size:0.9375rem; font-weight:400; text-transform:none; color:white; margin-top:15px" :disabled="!in_use">Unregister license</v-btn>
    <v-dialog v-model="dialog" width="640px">
      <v-card style="background-color:#fffcfa">
        <v-toolbar dense flat color="#f5983b">
          <v-toolbar-title class="white--text text-body-1 font-weight-medium">Unregister license</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:15px">
          <div class="text-body-1" style="color:black">Do you want to unregister your license to be used in another device?</div>
          <v-divider style="margin-top:15px"></v-divider>
          <v-row no-gutters style="margin-top:15px;">
            <v-btn :loading="loading" color="#20bf6b" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitUnregister">Confirm</v-btn>
            <v-btn :disabled="loading" color="#eb4d4b" @click="dialog = false" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
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
    item: '',
    showSecretKey: false,
    dialog: false,
  }),
  props: {
    account: Object
  },
  computed: {
    email() {
      if (this.account === undefined || this.account.profile === undefined) return ''
      else return this.account.profile.email
    },
    access_key() {
      if (this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.access_key
    },
    secret_key() {
      if (this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.secret_key
    },
    in_use() {
      if (this.account === undefined || this.account.license === undefined) return null
      return this.account.license.in_use
    }
  },
  methods: {
    submitUnregister() {
      this.loading = true
      axios.post('/license/unregister')
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
    },
  },
}
</script>