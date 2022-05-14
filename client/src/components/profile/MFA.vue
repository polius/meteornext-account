<template>
  <div>
    <div class="text-h6 font-weight-medium">Multi-factor authentication</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">Multi-factor authentication adds an additional layer of security to your account by requiring more than just a password to log in.</div>
    <v-card v-if="mfa.mode == null" style="margin-bottom:20px; background-color:rgba(61, 61, 80, 0.75)">
      <v-row no-gutters align="center" justify="center">
        <v-col cols="auto" style="display:flex; margin:15px">
          <v-icon color="#20bf6b" size="20">fas fa-shield-alt</v-icon>
        </v-col>
        <v-col>
          <div class="text-body-1" style="color:#e2e2e2">Protect your account by requiring an additional layer of security to sign in.</div>
        </v-col>
      </v-row>
    </v-card>
    <v-card v-else style="margin-bottom:20px">
      <v-row no-gutters>
        <v-col cols="auto" style="display:flex; margin:15px">
          <v-icon color="#20bf6b" size="20">fas fa-check-circle</v-icon>
        </v-col>
        <v-col style="padding-top:5px">
          <div class="text-body-1" style="color:#20bf6b">{{ `The MFA (${mfa.mode == '2fa' ? '2FA' : 'Security Key'}) is currently enabled.` }}</div>
          <div class="text-body-2" style="color:#e2e2e2; padding-bottom:5px">Active since: {{ dateFormat(mfa.created) }}</div>
        </v-col>
      </v-row>
    </v-card>
    <v-btn v-if="mfa.mode != null" :loading="loading" color="#f18805" @click="mfaDialog = true" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white;">Disable MFA</v-btn>
    <v-btn v-else :loading="loading" color="#2196f3" @click="mfaDialog = true" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white;">Enable MFA</v-btn>
    <v-dialog v-model="mfaDialog" width="672px">
      <v-card>
        <v-toolbar dense flat color="rgb(50, 50, 60)" style="border:solid rgba(255, 255, 255, 0.12) 1px">
          <v-toolbar-title class="text-body-1" style="color:#e2e2e2">Multi-factor authentication</v-toolbar-title>
          <v-divider v-if="mfa.mode != null || mfaDialogStep == 2" class="mx-3" inset vertical></v-divider>
          <div v-if="mfa.mode == '2fa' || (mfaDialogStep == 2 && mfaMode == '2fa')" class="text-body-1" style="color:#e2e2e2">Virtual 2FA Device</div>
          <div v-if="mfa.mode == 'webauthn' || (mfaDialogStep == 2 && mfaMode == 'webauthn')" class="text-body-1" style="color:#e2e2e2">Security Key</div>
        </v-toolbar>
        <v-card-text style="padding:15px; background-color:rgb(65, 65, 75); border:solid rgba(255, 255, 255, 0.12) 1px; border-top:0px">
          <v-container style="padding:0px">
            <v-layout wrap>
              <v-flex xs12>
                <v-form ref="mfaForm" @submit.prevent style="margin-bottom:15px">
                  <div v-if="mfa.mode == null">
                    <div v-if="mfaDialogStep == 1">
                      <div class="text-body-1" style="color:#e2e2e2">Choose the type of MFA device to assign:</div>
                      <v-radio-group v-model="mfaMode" hide-details style="margin-top:10px">
                        <v-radio value="2fa">
                          <template v-slot:label>
                            <div>
                              <div class="white--text">Virtual 2FA Device</div>
                              <div class="font-weight-regular caption" style="font-size:0.85rem !important">Authenticator app installed on your mobile device or computer</div>
                            </div>
                          </template>
                        </v-radio>
                        <v-radio value="webauthn" style="margin-top:5px">
                          <template v-slot:label>
                            <div>
                              <div class="white--text">Security Key</div>
                              <div class="font-weight-regular caption" style="font-size:0.85rem !important">YubiKey or any other compliant device</div>
                            </div>
                          </template>
                        </v-radio>
                      </v-radio-group>
                    </div>
                    <div v-else>
                      <v-alert dense v-if="mfaMode == 'webauthn' && webauthn.status == 'ko'" color="#EF5354">{{ webauthn.error }}</v-alert>
                      <v-card v-if="mfaMode == '2fa'">
                        <v-card-text style="background-color:rgb(60, 60, 70); padding:0px">
                          <v-row no-gutters>
                            <v-col style="margin:15px">
                              <v-progress-circular v-if="twoFactor['uri'] == null" indeterminate style="margin-left:auto; margin-right:auto; display:table;"></v-progress-circular>
                              <qrcode-vue v-else :value="twoFactor['uri']" size="200" level="H" background="#e2e2e2" foreground="#000000" style="text-align:center"></qrcode-vue>
                              <v-btn @click="twoFactorCodeDialog = true" text block hide-details color="#e2e2e2">CAN'T SCAN THE QR?</v-btn>
                              <v-text-field ref="twoFactorCode" outlined v-model="twoFactor['value']" v-on:keyup.enter="submitMFA" label="MFA Code" maxlength="6" :rules="[v => v == parseInt(v) && v >= 0 || '']" required hide-details style="margin-top:10px"></v-text-field>
                            </v-col>
                            <v-col style="margin:15px">
                              <div class="text-body-1 font-weight-regular" style="margin-bottom:20px; color:#e2e2e2">How to enable app based authentication</div>
                              <div class="text-body-1 font-weight-light" style="margin-bottom:15px"><span class="font-weight-regular">1.</span> Download and install an app (such as Google Authenticator) on your mobile device.</div>
                              <div class="text-body-1 font-weight-light" style="margin-bottom:15px"><span class="font-weight-regular">2.</span> Scan the QR code.</div>
                              <div class="text-body-1 font-weight-light"><span class="font-weight-regular">3.</span> Enter and verify the authentication code generated by the app.</div>
                            </v-col>
                          </v-row>
                        </v-card-text>
                      </v-card>
                      <v-card v-else-if="mfaMode == 'webauthn'">
                        <v-progress-linear v-show="loadingFingerprint" indeterminate></v-progress-linear>
                        <v-card-text style="background-color:rgb(60, 60, 70)">
                          <div class="text-h5 font-weight-light white--text" style="text-align:center; font-size:1.4rem !important">Verify your identity</div>
                          <v-icon :style="`display:table; margin-left:auto; margin-right:auto; margin-top:20px; margin-bottom:20px; color:${ webauthn.status == 'init' ? '#046cdc' : webauthn.status == 'ok' ? '#20bf6b' : webauthn.status == 'ko' ? '#ff5252' : '#fa8131'}`" size="55">fas fa-fingerprint</v-icon>
                          <div class="text-body-1" style="text-align:center; font-size:1.1rem !important; color:#e2e2e2">{{ ['init','validating'].includes(webauthn.status) ? 'Touch sensor' : webauthn.status == 'ok' ? 'Fingerprint recognized' : 'Fingerprint not recognized' }}</div>
                        </v-card-text>
                      </v-card>
                    </div>
                  </div>
                  <div v-else>
                    <div class="text-body-1">Are you sure you want to disable the MFA method?</div>
                  </div>
                </v-form>
                <v-divider></v-divider>
                <v-row no-gutters style="margin-top:20px;">
                  <v-btn :disabled="mfa.mode == null && mfaDialogStep == 2 && mfaMode == 'webauthn' && webauthn.status != 'ok'" :loading="loading" color="primary" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitMFA">{{ mfa.mode ? 'Disable MFA' : 'Confirm' }}</v-btn>
                  <v-btn :disabled="loading" text color="white" @click="cancelMFA" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
                </v-row>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-dialog v-model="twoFactorCodeDialog" width="512px">
      <v-card>
        <v-toolbar dense flat color="#f5983b">
          <v-toolbar-title class="white--text text-body-1">QR CODE</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="background-color:#fffcfa; padding:0px">
          <v-container>
            <v-layout wrap>
              <v-flex xs12>
                <div style="font-size:18px; letter-spacing:0.08em; text-align:center;">{{ twoFactor['hash'] }}</div>
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
      axios.get('/2fa')
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
          EventBus.$emit('send-notification', response.data.message, '#20bf6b')
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
      axios.post('/2fa', payload)
        .then((response) => {
          this.mfaDialog = false
          this.getMFA()
          EventBus.$emit('send-notification', response.data.message, '#20bf6b')
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
        EventBus.$emit('send-notification', response.data.message, '#20bf6b')
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