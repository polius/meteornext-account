<template>
  <div style="height:100%">
    <v-main :style="{ height:'100%', padding:'0px', backgroundImage: 'url(' + require('@/assets/bg.jpg') + ')', backgroundRepeat: 'no-repeat', backgroundSize: 'cover' }">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <v-card style="border-radius:5px">
                <v-card-text>
                  <v-avatar :size="130" style="margin-top:10px;"><img :src="require('../assets/logo.png')" /></v-avatar>
                  <div class="display-2" style="color:rgba(255,255,255,.9); margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline" style="font-size:1.3rem!important; color:rgba(255,255,255,.9); margin-top:10px; margin-bottom:20px">ACCOUNT</div>
                  <v-divider></v-divider>
                  <v-form ref="form" @submit.prevent style="margin-top:20px">
                    <div v-if="mfa == '2fa'">
                      <v-text-field ref="2fa" filled v-model="twoFactor['value']" label="2FA Code" maxlength="6" :rules="[v => !!v || '']" v-on:keyup.enter="login()" style="margin-bottom:20px;" hide-details>
                        <template v-slot:append><v-icon small style="margin-top:3px; margin-right:4px">fas fa-key</v-icon></template>
                      </v-text-field>
                    </div>
                    <div v-else>
                      <v-text-field ref="email" filled v-model="email" name="email" label="Email" :rules="[v => !!v || '']" required v-on:keyup.enter="login()" style="margin-bottom:20px;" hide-details>
                        <template v-slot:append><v-icon small style="margin-top:4px; margin-right:4px">fas fa-user</v-icon></template>
                      </v-text-field>
                      <v-text-field ref="password" filled v-model="password" name="password" label="Password" :rules="[v => !!v || '']" required type="password" v-on:keyup.enter="login()" style="margin-bottom:20px;" hide-details>
                        <template v-slot:append><v-icon small style="margin-top:4px; margin-right:4px">fas fa-lock</v-icon></template>
                      </v-text-field>
                    </div>
                  </v-form>
                  <v-btn x-large type="submit" color="info" :loading="loading" block style="margin-top:0px;" @click="login()">LOGIN</v-btn>
                  <v-btn text block style="margin-top:10px">Create account</v-btn>
                </v-card-text>
              </v-card>
            </v-slide-y-transition>
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
    <v-snackbar v-model="snackbar" :multi-line="false" :timeout="snackbarTimeout" :color="snackbarColor" top style="padding-top:0px;">
      {{ snackbarText }}
      <template v-slot:action="{ attrs }">
        <v-btn color="white" text v-bind="attrs" @click="snackbar = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
// import axios from 'axios'

export default {
  data: () => ({
    loading: false,
    // Login Form
    email: '',
    password: '',
    mfa: null,

    // MFA Dialog
    mfaDialog: false,
    twoFactor: {
      hash: null,
      uri: null,
      value: ''
    },

    // Snackbar
    snackbar: false,
    snackbarTimeout: Number(3000),
    snackbarColor: '',
    snackbarText: ''
  }),
  props: ['url'],
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
        this.notification('Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      var payload = {
        email: this.email,
        password: this.password,
      }
      if (this.twoFactor['value'].length > 0) payload['mfa'] = this.twoFactor['value']
      if (this.twoFactor['hash'] != null) payload['2fa_hash'] = this.twoFactor['hash']
      try {
        let response = await this.$store.dispatch('app/login', payload)
        this.loading = false
        if (response.status == 200) this.$router.push('/')
        else if (response.status == 202) {
          this.password = this.passwordItem.new.length > 0 ? this.passwordItem.new : this.password
          payload['password'] = this.password
          // MFA Required
          if (response.data.code == 'mfa_setup') this.mfaDialog = true
          else if (['2fa','webauthn'].includes(response.data.code)) {
            delete payload['currentPassword']
            delete payload['newPassword']
            delete payload['repeatPassword']
            this.mfa = response.data.code
          }
        }
      }
      catch (error) {
        this.loading = false
        if (error.response === undefined) this.notification("Can't establish a connection to the server", '#EF5354')
        else this.notification(error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
      }
    },
    notification(message, color) {
      this.snackbarText = message
      this.snackbarColor = color 
      this.snackbar = true
    }
  }
}
</script>