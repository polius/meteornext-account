<template>
  <div style="height:100%">
    <v-main :style="{ height:'100%', padding:'0px', backgroundImage: 'url(' + require('@/assets/bg.jpg') + ')', backgroundRepeat: 'no-repeat', backgroundSize: 'cover' }">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <v-card style="border-radius:5px">
                <v-card-text>
                  <v-avatar :size="130" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                  <div class="display-2" style="color:black; margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline" style="font-size:1.3rem!important; color:black; margin-top:10px; margin-bottom:20px">ACCOUNT | LOGIN</div>
                  <v-divider></v-divider>
                  <v-form ref="form" @submit.prevent style="margin-top:20px">
                    <div v-if="mfa == '2fa'">
                      <v-text-field ref="2fa" filled v-model="twoFactor['value']" label="2FA Code" maxlength="6" :rules="[v => !!v || '']" v-on:keyup.enter="login()" style="margin-bottom:20px;" hide-details>
                        <template v-slot:append><v-icon small style="margin-top:3px; margin-right:4px">fas fa-key</v-icon></template>
                      </v-text-field>
                    </div>
                    <div v-else-if="mfa == 'webauthn'">
                      <v-card>
                        <v-progress-linear v-show="loading" indeterminate></v-progress-linear>
                        <v-card-text>
                          <div class="text-h5 font-weight-light" style="color:black; text-align:center; font-size:1.4rem !important">Verify your identity</div>
                          <v-icon :style="`display:table; margin-left:auto; margin-right:auto; margin-top:20px; margin-bottom:20px; color:${ webauthn.status == 'init' ? '#046cdc' : webauthn.status == 'ok' ? '#00b16a' : webauthn.status == 'ko' ? '#ff5252' : '#fa8131'}`" size="55">fas fa-fingerprint</v-icon>
                          <div class="text-subtitle-1" style="color:black; text-align:center; font-size:1.1rem !important;">{{ ['init','validating'].includes(webauthn.status) ? 'Touch sensor' : webauthn.status == 'ok' ? 'Fingerprint recognized' : 'Fingerprint not recognized' }}</div>
                        </v-card-text>
                      </v-card>
                    </div>
                    <div v-else>
                      <v-text-field ref="email" filled v-model="email" name="email" label="Email" :rules="[v => !!v || '']" required v-on:keyup.enter="login()" style="margin-bottom:20px" hide-details autofocus></v-text-field>
                      <v-text-field ref="password" filled v-model="password" name="password" label="Password" :rules="[v => !!v || '']" required type="password" v-on:keyup.enter="login()" hide-details></v-text-field>
                      <p style="margin-top:8px; margin-bottom:8px; text-align:right"><span @click="resetPassword" class="link">Forgot password?</span></p>
                    </div>
                  </v-form>
                  <v-btn v-if="!(mfa == 'webauthn')" x-large type="submit" color="info" :loading="loading" block style="margin-top:0px;" @click="login()">LOGIN</v-btn>
                  <div v-if="!(mfa == 'webauthn')" class="text-body-2" style="color:black; margin-top:15px">Don't have an account? <router-link to="/register" style="text-decoration:none; font-weight:500">Sign up</router-link></div>
                </v-card-text>
              </v-card>
            </v-slide-y-transition>
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
  </div>
</template>

<style scoped>
.link:hover {
  color: #1976d2;
  cursor: pointer;
}
</style>

<script>
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
    prevRoute: null
  }),
  props: ['url'],
  beforeRouteEnter(to, from, next) {
    next(vm => {
      vm.prevRoute = from
    })
  },
  mounted() {
    if (this.prevRoute.name == 'verifyEmail') EventBus.$emit('send-notification', 'Account Verified', '#00b16a')
    else if (this.prevRoute.name == 'resetPasswordCode') EventBus.$emit('send-notification', 'Password Updated', '#00b16a')
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
        if (response.status == 200) this.$router.push('/')
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
                this.$router.push('/')
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
        else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
      }
    },
    resetPassword() {
      this.$router.push('/reset_password')
    },
  }
}
</script>