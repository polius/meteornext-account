<template>
  <div style="height:100%">
    <v-main style="height:100%">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <v-card style="border-radius:5px; background-color:rgba(61, 61, 80, 0.7)">
                <v-card-text>
                  <v-avatar :size="100" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                  <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | LOGIN</div>
                  <v-divider></v-divider>
                  <v-form ref="form" @submit.prevent style="margin-top:20px">
                    <div v-if="mfa == '2fa'">
                      <v-text-field ref="2fa" filled v-model="twoFactor['value']" label="2FA Code" maxlength="6" :rules="[v => !!v || '']" v-on:keyup.enter="login()" style="margin-bottom:20px;" hide-details></v-text-field>
                    </div>
                    <div v-else-if="mfa == 'webauthn'">
                      <v-card style="background-color:rgba(255,255,255,0.1)">
                        <v-progress-linear v-show="loading" indeterminate></v-progress-linear>
                        <v-card-text>
                          <div class="text-h5 font-weight-light white--text" style="text-align:center; font-size:1.4rem !important">Verify your identity</div>
                          <v-icon :style="`display:table; margin-left:auto; margin-right:auto; margin-top:20px; margin-bottom:20px; color:${ webauthn.status == 'init' ? '#2196f3' : webauthn.status == 'ok' ? '#20bf6b' : webauthn.status == 'ko' ? '#ff5252' : '#fa8131'}`" size="55">fas fa-fingerprint</v-icon>
                          <div class="text-body-1" style="text-align:center; font-size:1.1rem !important; color:#e2e2e2">{{ ['init','validating'].includes(webauthn.status) ? 'Touch sensor' : webauthn.status == 'ok' ? 'Fingerprint recognized' : 'Fingerprint not recognized' }}</div>
                        </v-card-text>
                      </v-card>
                    </div>
                    <div v-else>
                      <v-text-field ref="email" filled v-model="email" name="email" label="Email" type="email" :rules="[v => !!v || '']" required v-on:keyup.enter="login()" style="margin-bottom:20px" hide-details autofocus></v-text-field>
                      <v-text-field ref="password" filled v-model="password" name="password" label="Password" :rules="[v => !!v || '']" required type="password" v-on:keyup.enter="login()" hide-details></v-text-field>
                      <p style="margin-top:8px; margin-bottom:8px; text-align:right; color:#e2e2e2"><span @click="resetPassword" class="link">Forgot password?</span></p>
                    </div>
                  </v-form>
                  <v-btn v-if="!(mfa == 'webauthn')" x-large type="submit" color="info" :loading="loading" block style="margin-top:0px;" @click="login()">LOGIN</v-btn>
                  <div v-if="!(mfa == 'webauthn')" class="text-body-2" style="margin-top:15px; color:#e2e2e2; font-size:15px!important">Don't have an account? <router-link to="/register" style="text-decoration:none; font-weight:500; color:white">Sign up</router-link></div>
                </v-card-text>
              </v-card>
            </v-slide-y-transition>
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
    <v-snackbar v-model="snackbar" :multi-line="false" :timeout="Number(3000)" color="info" top style="padding-top:0px;">
      Please verify your email address
      <template v-slot:action="{ attrs }">
        <v-btn text v-bind="attrs" @click="sendVerifyMail">Resend email</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<style scoped>
.link:hover {
  color: #2196f3;
  cursor: pointer;
}
</style>

<script>
import axios from 'axios'
import EventBus from '../js/event-bus'
import { webauthnLogin } from '../plugins/webauthn.js'

export default {
  data: () => ({
    loading: false,
    // Login Form
    email: '',
    password: '',
    mfa: null,
    // MFA
    twoFactor: {
      hash: null,
      uri: null,
      value: ''
    },
    webauthn: { 
      status: 'init'
    },
    // Previous route
    prevRoute: null,
    // Snackbar
    snackbar: false,
  }),
  props: ['url'],
  beforeRouteEnter(to, from, next) {
    next(vm => {
      vm.prevRoute = from
    })
  },
  mounted() {
    if (this.prevRoute.name == 'verifyEmail') EventBus.$emit('send-notification', 'Email verified', '#20bf6b')
    else if (this.prevRoute.name == 'resetPasswordCode') EventBus.$emit('send-notification', 'Password updated', '#20bf6b')
  },
  watch: {
    mfa: function (val) {
      if (val == '2fa') {
        this.$nextTick(() => { 
          this.$refs['2fa'].focus()
          this.$refs.form.resetValidation()
        })
      }
    }
  },
  methods: {
    async login() {
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      this.webauthn = { status: 'init' }
      var payload = {
        email: this.email,
        password: this.password
      }
      if (this.twoFactor['value'].length > 0) payload['mfa'] = this.twoFactor['value']
      if (this.twoFactor['hash'] != null) payload['2fa_hash'] = this.twoFactor['hash']
      try {
        let response = await this.$store.dispatch('app/login', payload)
        this.loading = false
        if (response.status == 200) this.loginSuccess()
        else if (response.status == 202) {
          // MFA Required
          if (['2fa','webauthn'].includes(response.data.code)) {
            delete payload['currentPassword']
            delete payload['newPassword']
            delete payload['repeatPassword']
            this.mfa = response.data.code
            if (this.mfa == 'webauthn') {
              try {
                let mfa = await webauthnLogin(response.data.data)
                this.loading = true
                this.webauthn = { status: 'validating' }
                await this.$store.dispatch('app/login', { ...payload, mfa, host: window.location.host })
                this.loginSuccess()
              }
              catch (error) {
                this.loading = true
                this.webauthn = { status: 'ko' }
                EventBus.$emit('send-notification', 'response' in error ? error.response.data.message : error.message, '#EF5354')
                setTimeout(() => { this.loading = false; this.mfa = null }, 1000)
              }
            }
          }
        }
      }
      catch (error) {
        this.loading = false
        if (error.response === undefined)  EventBus.$emit('send-notification', "Can't establish a connection to the server", '#EF5354')
        else if (error.response.data.message !== undefined) {
          if (error.response.data.message == 'Please verify your email address') this.snackbar = true
          else EventBus.$emit('send-notification', error.response.data.message, '#EF5354')
        }
        else EventBus.$emit('send-notification', 'Internal Server Error', '#EF5354')
      }
    },
    loginSuccess() {
      if (this.$route.query.url !== undefined) this.$router.push({ path: this.$route.query.url })
      else this.$router.push('/')
    },
    resetPassword() {
      this.$router.push({ name: 'resetPassword' })
    },
    sendVerifyMail() {
      this.snackbar = false
      const payload = { 'email': this.email }
      axios.post('/account/email/resend', payload)
        .then((response) => {
          EventBus.$emit('send-notification', response.data.message, '#20bf6b')
        })
        .catch((error) => {
          EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
    },
  }
}
</script>