<template>
  <div>
    <div class="text-h6 font-weight-medium">Multi factor security</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">Multi-factor authentication adds an additional layer of security to your account by requiring more than just a password to log in.</div>
    <v-card v-if="mfa.mode == null" style="margin-bottom:20px">
      <v-row no-gutters align="center" justify="center">
        <v-col cols="auto" style="display:flex; margin:15px">
          <v-icon color="#00b16a">fas fa-shield-alt</v-icon>
        </v-col>
        <v-col>
          <div class="text-body-1">Protect your account by requiring an additional layer of security to sign in.</div>
        </v-col>
      </v-row>
    </v-card>
    <v-card v-else style="margin-bottom:20px">
      <v-row no-gutters>
        <v-col cols="auto" style="display:flex; margin:15px">
          <v-icon color="#00b16a">fas fa-check-circle</v-icon>
        </v-col>
        <v-col style="padding-top:5px">
          <div class="text-body-1" style="color:#00b16a">{{ `The MFA (${mfa.mode == '2fa' ? '2FA' : 'Security Key'}) is currently enabled.` }}</div>
          <div class="text-body-2">Active since: {{ dateFormat(mfa.created) }}</div>
        </v-col>
      </v-row>
    </v-card>
    <v-btn v-if="mfa.mode != null" :loading="loading" color="warning" @click="mfaDialog = true" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white;">Disable MFA</v-btn>
    <v-btn v-else :loading="loading" color="#2196f3" @click="mfaDialog = true" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white;">Enable MFA</v-btn>
    <v-dialog v-model="mfaDialog" max-width="672px">
      <v-card style="background-color:#fffcfa">
        <v-toolbar dense flat color="#f5983b">
          <v-toolbar-title class="white--text subtitle-1">Two factor security</v-toolbar-title>
          <v-divider v-if="mfa.mode != null || mfaDialogStep == 2" class="mx-3" inset vertical></v-divider>
          <div v-if="mfa.mode == '2fa' || (mfaDialogStep == 2 && mfaMode == '2fa')" class="text-body-1 white--text">Virtual 2FA Device</div>
          <div v-if="mfa.mode == 'webauthn' || (mfaDialogStep == 2 && mfaMode == 'webauthn')" class="text-body-1 white--text">Security Key</div>
          <v-spacer></v-spacer>
          <v-btn @click="mfaDialog = false" icon><v-icon style="font-size:22px; color:white">fas fa-times-circle</v-icon></v-btn>
        </v-toolbar>
        <v-card-text style="padding:15px">
          <v-container style="padding:0px">
            <v-layout wrap>
              <v-flex xs12>
                <v-form ref="mfaForm" @submit.prevent style="margin-bottom:15px">
                  <div v-if="mfa.mode == null">
                    <div v-if="mfaDialogStep == 1">
                      <div class="text-body-1" style="color:black">Choose the type of MFA device to assign:</div>
                      <v-radio-group v-model="mfaMode" hide-details style="margin-top:10px">
                        <v-radio value="2fa">
                          <template v-slot:label>
                            <div>
                              <div style="color:black">Virtual 2FA Device</div>
                              <div class="font-weight-regular caption" style="font-size:0.85rem !important">Authenticator app installed on your mobile device or computer</div>
                            </div>
                          </template>
                        </v-radio>
                        <v-radio value="webauthn" style="margin-top:5px">
                          <template v-slot:label>
                            <div>
                              <div style="color:black">Security Key</div>
                              <div class="font-weight-regular caption" style="font-size:0.85rem !important">YubiKey or any other compliant device</div>
                            </div>
                          </template>
                        </v-radio>
                      </v-radio-group>
                    </div>
                    <div v-else>
                      <v-alert dense v-if="mfaMode == 'webauthn' && webauthn.status == 'ko'" color="#EF5354">{{ webauthn.error }}</v-alert>
                      <v-card v-if="mfaMode == '2fa'">
                        <v-card-text style="padding:0px">
                          <v-row no-gutters>
                            <v-col style="margin:15px">
                              <v-progress-circular v-if="twoFactor['uri'] == null" indeterminate style="margin-left:auto; margin-right:auto; display:table;"></v-progress-circular>
                              <qrcode-vue v-else :value="twoFactor['uri']" size="200" level="H" background="#ffffff" foreground="#000000" style="text-align:center"></qrcode-vue>
                              <v-btn @click="twoFactorCodeDialog = true" text block hide-details>CAN'T SCAN THE QR?</v-btn>
                              <v-text-field ref="twoFactorCode" outlined v-model="twoFactor['value']" v-on:keyup.enter="submitMFA" label="MFA Code" maxlength="6" :rules="[v => v == parseInt(v) && v >= 0 || '']" required hide-details style="margin-top:10px">
                                <template v-slot:append><v-icon small style="margin-top:3px; margin-right:4px">fas fa-key</v-icon></template>
                              </v-text-field>
                            </v-col>
                            <v-col style="margin:15px">
                              <div class="text-body-1 font-weight-regular" style="color:black; margin-bottom:20px">How to enable app based authentication</div>
                              <div class="text-body-1 font-weight-light" style="color:black; margin-bottom:15px">1. Download and install an app (such as Google Authenticator) on your mobile device.</div>
                              <div class="text-body-1 font-weight-light" style="color:black; margin-bottom:15px">2. Scan the QR code.</div>
                              <div class="text-body-1 font-weight-light" style="color:black">3. Enter and verify the authentication code generated by the app.</div>
                            </v-col>
                          </v-row>
                        </v-card-text>
                      </v-card>
                      <v-card v-else-if="mfaMode == 'webauthn'">
                        <v-progress-linear v-show="loadingFingerprint" indeterminate></v-progress-linear>
                        <v-card-text>
                          <div class="text-h5 font-weight-light" style="color:black; text-align:center; font-size:1.4rem !important">Verify your identity</div>
                          <v-icon :style="`display:table; margin-left:auto; margin-right:auto; margin-top:20px; margin-bottom:20px; color:${ webauthn.status == 'init' ? '#046cdc' : webauthn.status == 'ok' ? '#00b16a' : webauthn.status == 'ko' ? '#ff5252' : '#fa8131'}`" size="55">fas fa-fingerprint</v-icon>
                          <div class="text-subtitle-1" style="color:black; text-align:center; font-size:1.1rem !important;">{{ ['init','validating'].includes(webauthn.status) ? 'Touch sensor' : webauthn.status == 'ok' ? 'Fingerprint recognized' : 'Fingerprint not recognized' }}</div>
                        </v-card-text>
                      </v-card>
                    </div>
                  </div>
                  <div v-else>
                    <v-card>
                      <v-row no-gutters>
                        <v-col cols="auto" style="display:flex; margin:15px">
                          <v-icon color="#00b16a">fas fa-check-circle</v-icon>
                        </v-col>
                        <v-col style="padding-top:5px">
                          <div class="text-body-1" style="color:#00b16a">The MFA is currently enabled.</div>
                          <div class="text-body-2">Active since: {{ dateFormat(mfa.created) }}</div>
                        </v-col>
                      </v-row>
                    </v-card>
                  </div>
                </v-form>
                <v-divider></v-divider>
                <v-row no-gutters style="margin-top:20px;">
                  <v-btn :disabled="mfa.mode == null && mfaDialogStep == 2 && mfaMode == 'webauthn' && webauthn.status != 'ok'" :loading="loading" color="#00b16a" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitMFA">{{ mfa.mode ? 'Disable MFA' : 'Confirm' }}</v-btn>
                  <v-btn :disabled="loading" color="#e74c3c" @click="cancelMFA" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
                </v-row>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-model="twoFactorCodeDialog" max-width="512px">
      <v-card>
        <v-toolbar dense flat color="primary">
          <v-toolbar-title class="white--text subtitle-1"><v-icon small color="white" style="margin-right:10px; margin-bottom:3px">fas fa-qrcode</v-icon>QR CODE</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:0px">
          <v-container>
            <v-layout wrap>
              <v-flex xs12>
                <div style="color:black; font-size:18px; letter-spacing:0.08em; text-align:center;">{{ twoFactor['hash'] }}</div>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import EventBus from '../../js/event-bus.js'

import { webauthnRegisterBegin, webauthnRegisterValidate, webauthnRegisterFinish } from '../../plugins/webauthn.js'
import axios from 'axios'
import moment from 'moment'
import QrcodeVue from 'qrcode.vue'

export default {
  data: () => ({
    mfaDialog: false,
    mfa: { mode: null, created: null },

    // Loading
    loading: false,
    loadingFingerprint: false,

    // MFA Dialog
    mfaDialogStep: 1,
    mfaMode: '2fa',
    twoFactorCodeDialog: false,
    twoFactor: {
      hash: null,
      uri: null,
      value: ''
    },
    webauthn: {
      status: 'init',
      error: '',
      credentials: null
    },
  }),
  props: { 
    account: Object,
  },
  components: { QrcodeVue },
  created() {
    this.getMFA()
  },
  watch: {
    mfaDialog: function (val) {
      if (val && this.mfa.mode == null) this.get2FA()
      else {
        requestAnimationFrame(() => {
          this.mfaDialogStep = 1
          this.mfaMode = '2fa'
        })
      }
    },
    mfaDialogStep: function (val) {
      if (val == 2) {
        requestAnimationFrame(() => {
          if (typeof this.$refs.mfaForm !== 'undefined') this.$refs.mfaForm.resetValidation()
          if (typeof this.$refs.twoFactorCode !== 'undefined') this.$refs.twoFactorCode.focus()
        })
      }
    },
    twoFactorCodeDialog: function(val) {
      requestAnimationFrame(() => {
        if (typeof this.$refs.mfaForm !== 'undefined') this.$refs.mfaForm.resetValidation()
        if (!val && typeof this.$refs.twoFactorCode !== 'undefined') this.$refs.twoFactorCode.focus()
      })
    },
  },
  methods: {
    getMFA() {
      this.loading = true
      axios.get('/mfa')
        .then((response) => {
          this.mfa = response.data.data
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    get2FA() {
      this.twoFactor = { hash: null, uri: null, value: '' }
      axios.get('/mfa/2fa')
        .then((response) => {
          this.twoFactor['hash'] = response.data['mfa_hash']
          this.twoFactor['uri'] = response.data['mfa_uri']
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
    },
    async getWebauthn() {
      this.webauthn = { status: 'init', error: '', credentials: null }
      try {
        const credentials = await webauthnRegisterBegin()
        this.loadingFingerprint = true
        this.webauthn = { status: 'validating', error: '', credentials }
      }
      catch (error) {
        if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
        this.webauthn = { status: 'ko', error: error.response.data.message, credentials: null }
      }
      try {
        await webauthnRegisterValidate(this.webauthn.credentials)
        this.webauthn['status'] = 'ok'
      }
      catch (error) {
        if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
        this.webauthn = { status: 'ko', error: error.response.data.message, credentials: null }
      }
      this.loadingFingerprint = false
    },
    submitMFA() {
      if (this.mfa.mode) this.disableMFA()
      else this.enableMFA()
    },
    cancelMFA() {
      if (this.mfaDialogStep == 2) this.mfaDialogStep = 1
      else this.mfaDialog = false
    },
    enableMFA() {
      if (this.mfaDialogStep == 1) {
        this.mfaDialogStep = 2
        if (this.mfaMode == 'webauthn') this.getWebauthn()
      }
      else if (this.mfaMode == '2fa') this.enable2FA()
      else if (this.mfaMode == 'webauthn') this.enableWebauthn()
    },
    disableMFA() {
      this.loading = true
      axios.delete('/mfa')
        .then((response) => {
          this.mfaDialog = false
          this.getMFA()
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    enable2FA() {
      // Check if all fields are filled
      if (!this.$refs.mfaForm.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      let payload = {'hash': this.twoFactor.hash, 'value': this.twoFactor.value}
      axios.post('/mfa/2fa', payload)
        .then((response) => {
          this.mfaDialog = false
          this.getMFA()
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    enableWebauthn() {
      this.loading = true
      webauthnRegisterFinish(this.webauthn.credentials)
      .then((response) => {
        this.mfaDialog = false
        this.getMFA()
        EventBus.$emit('send-notification', response.data.message, '#00b16a')
      })
      .catch((error) => {
        if ([401,422,503].includes(error.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
        this.webauthn = { status: 'ko', error: error.response.data.message, credentials: null }
      })
      .finally(() => this.loading = false)
    },
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("YYYY-MM-DD HH:mm:ss")
      return date
    },
  }
}
</script>