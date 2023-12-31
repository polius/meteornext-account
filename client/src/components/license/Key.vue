<template>
  <div>
    <div class="text-h6 font-weight-medium">License key</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:10px">Use the following credentials to register your copy of Meteor Next.</div>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Access Key</div>
    <v-text-field :loading="account.license === undefined" flat @click="$event.target.select()" solo v-model="access_key" readonly class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <div class="text-body-2 font-weight-medium" style="margin-top:15px">Secret Key</div>
    <v-text-field :loading="account.license === undefined" flat @focus="showSecretKey = true" @blur="showSecretKey = false" @click="$event.target.select()" solo v-model="secret_key" readonly :type="showSecretKey ? 'text' : 'password'" class="no-edit" style="padding-top:5px" hide-details></v-text-field>
    <div v-show="in_use != null" class="body-1" style="margin-top:15px"><v-icon :style="`font-size:16px; margin-right:10px; margin-bottom:3px; color:${in_use ? '#ff8c00' : '#20bf6b'}`">fas fa-circle</v-icon>{{ in_use ? 'License registered.' : 'License ready to be registered.' }}</div>
    <div class="text-body-1 font-weight-light" style="margin-top:15px">A license key can be used only in one device. To be able to use it in another device, first you have to unregister it from the first one.</div>
    <v-btn :disabled="!in_use" @click="dialog = true" color="info" title="Unregister your existing license to use it in another computer" style="font-size:0.95rem; letter-spacing:1px; font-weight:400; text-transform:none; color:white; margin-top:15px; margin-right:10px">Unregister license</v-btn>
    <v-btn text title="Go to the Meteor Next documentation" href="https://docs.meteornext.io/getting-started.html" target="_blank" style="font-size:0.95rem; letter-spacing:1px; font-weight:400; text-transform:none; color:white; margin-top:15px">Getting started</v-btn>
    <v-dialog v-model="dialog" width="640px">
      <v-card>
        <v-toolbar dense flat color="rgb(50, 50, 60)" style="border:solid rgba(255, 255, 255, 0.12) 1px">
          <v-toolbar-title class="white--text text-body-1 font-weight-regular">Unregister license</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:15px; background-color:rgb(65, 65, 75); border:solid rgba(255, 255, 255, 0.12) 1px; border-top:0px">
          <v-card style="background-color:rgb(60, 60, 70)">
            <v-row no-gutters align="center" justify="center">
              <v-col cols="auto" style="display:flex; margin:15px">
                <v-icon size="20" color="warning">fas fa-exclamation-triangle</v-icon>
              </v-col>
              <v-col>
                <div class="text-body-1" style="color:#e2e2e2">You can unregister the license once per hour.</div>
              </v-col>
            </v-row>
          </v-card>
          <div class="text-body-1" style="margin-top:15px">Do you want to unregister your license to be used in another device?</div>
          <v-divider style="margin-top:15px"></v-divider>
          <v-row no-gutters style="margin-top:15px;">
            <v-btn :loading="loading" color="primary" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitUnregister">Confirm</v-btn>
            <v-btn :disabled="loading" text color="white" @click="dialog = false" style="font-size:0.95rem; font-weight:400; text-transform:none; margin-left:5px">Cancel</v-btn>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
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
    item: '',
    showSecretKey: false,
    dialog: false,
  }),
  props: {
    account: Object
  },
  computed: {
    access_key() {
      if (this.account.license === undefined) return ''
      return this.account.license.access_key
    },
    secret_key() {
      if (this.account.license === undefined) return ''
      return this.account.license.secret_key
    },
    in_use() {
      if (this.account.license === undefined) return null
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