<template>
  <v-dialog v-model="dialog" max-width="640px">
    <v-card>
      <v-toolbar dense flat color="primary">
        <v-toolbar-title class="white--text subtitle-1">CHANGE LICENSE</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false" icon><v-icon style="font-size:22px">fas fa-times-circle</v-icon></v-btn>
      </v-toolbar>
      <v-card-text style="padding:15px">
        <v-container style="padding:0px">
          <v-layout wrap>
            <v-flex xs12>
              <v-form ref="form" @submit.prevent>
                <v-card>
                  <v-card-text>
                    <div class="text-h6 font-weight-light white--text">Current License</div>
                    <v-text-field readonly v-model="resources" label="Resources" :rules="[v => v == parseInt(v) && v > 0 || '']" style="padding-top:20px" hide-details></v-text-field>
                    <v-row no-gutters style="margin-top:20px">
                      <v-col cols="auto" style="margin-right:5px">
                        <div class="body-1 white--text">Price:</div>
                      </v-col>
                      <v-col>
                        <div class="body-1 white--text">{{ pricing }}</div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
                <v-card style="margin-top:15px">
                  <v-card-text>
                    <div class="text-h6 font-weight-light white--text">New License</div>
                    <v-text-field v-model="newLicense" label="Resources" :rules="[v => v == parseInt(v) && v > 0 || '']" style="padding-top:20px" autofocus hide-details></v-text-field>
                    <v-row no-gutters style="margin-top:20px">
                      <v-col cols="auto" style="margin-right:5px">
                        <div class="body-1 white--text">Price:</div>
                      </v-col>
                      <v-col>
                        <div class="body-1 white--text">{{ pricing }}</div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-form>
              <v-divider style="margin-top:15px"></v-divider>
              <v-row no-gutters style="margin-top:15px">
                <v-btn :disabled="newLicense == null || !parseInt(newLicense) || newLicense < 1 || newLicense == resources" :loading="loading" color="#00b16a" @click="submitChange">CONFIRM</v-btn>
                <v-btn :disabled="loading" color="#EF5354" @click="dialog = false" style="margin-left:5px">CANCEL</v-btn>
                <v-spacer/>
                <v-btn text :disabled="loading" color="primary" @click="dialog = false" style="margin-left:5px">{{ $vuetify.breakpoint.smAndDown ? 'INFO' : 'INFORMATION' }}</v-btn>
              </v-row>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    loading: false,
    newLicense: null,
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
    resources_label() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.resources + (this.account.license.resources == 1 ? ' Server' : ' Servers') + ' / User'
    },
    resources() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.resources
    },
    pricing() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      else if (this.account.license.price) return this.account.license.price + ' €'
      else return 'Free'
    },
  },
  methods: {
    submitChange() {
      this.loading = true
      axios.post('/account/change')
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
  watch: {
    dialog: function(val) {
      if (val) {
        this.newLicense = null // = { current: '', new: '', repeat: ''}
        requestAnimationFrame(() => {
          if (typeof this.$refs.form !== 'undefined') this.$refs.form.resetValidation()
          // if (typeof this.$refs.form !== 'undefined') this.$refs.passwordCurrent.focus()
        })
      }
    }
  },
}
</script>