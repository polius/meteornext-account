<template>
  <div style="height:100%">
    <v-main style="height:100%; padding:0px">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <v-card style="border-radius:5px; background-color:rgba(61, 61, 80, 0.8)">
                <v-card-text>
                  <v-avatar :size="100" style="margin-top:10px;"><img src="https://meteornext.io/assets/logo.png" /></v-avatar>
                  <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | REGISTER</div>
                  <v-divider></v-divider>
                  <div v-if="verify" style="margin-top:20px; margin-bottom:5px">
                    <div class="text-h6 white--text" style="font-weight:400">Verify your email</div>
                    <div class="text-body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px; color:#e2e2e2">We have sent an email to the address you entered</div>
                  </div>
                  <v-form v-else ref="form" @submit.prevent style="margin-top:20px">
                    <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">Full name</div>
                    <v-text-field ref="name" solo v-model="name" name="name" required style="padding-top:5px; margin-bottom:10px;" hide-details autofocus></v-text-field>
                    <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">Email</div>
                    <v-text-field ref="email" solo v-model="email" name="email" type="email" :rules="emailRules" required style="padding-top:5px; margin-bottom:10px;" hide-details></v-text-field>
                    <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">Password</div>
                    <v-text-field ref="password" solo v-model="password" name="password" :rules="[v => !!v || '']" required type="password" style="padding-top:5px; margin-bottom:10px;" hide-details></v-text-field>
                    <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">Repeat Password</div>
                    <v-text-field ref="password2" solo v-model="password2" name="password2" :rules="[v => !!v || '']" required type="password" style="padding-top:5px; margin-bottom:10px;" hide-details></v-text-field>
                    <div class="text-body-2" style="margin-top:10px; text-align:left; color:#e2e2e2">Use 8 or more characters with a mix of letters and numbers.</div>
                    <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">Confirm Captha</div>
                    <vue-hcaptcha ref="captcha" data-theme="dark" sitekey="d4fcdf7d-363a-495b-8e51-aff6e138aa6c" @verify="onVerify" style="padding-top:5px; text-align:left"></vue-hcaptcha>
                    <v-btn x-large type="submit" color="info" :loading="loading" block style="margin-top:10px;" @click="register()">CREATE ACCOUNT</v-btn>
                    <div class="text-body-2" style="margin-top:15px; color:#e2e2e2; font-size:15px !important">Have an account? <router-link to="/login" style="text-decoration:none; font-weight:500; color:white">Sign in</router-link></div>
                  </v-form>
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
</style>

<script>
import VueHcaptcha from '@hcaptcha/vue-hcaptcha';
import axios from 'axios'
import EventBus from '../js/event-bus'

export default {
  data: () => ({
    loading: false,
    emailRules: [
      v => !!v || "E-mail is required",
      v => /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(v) || 'E-mail must be valid',
    ],
    name: '',
    email: '',
    password: '',
    password2: '',
    token: '',
    verify: false,
  }),
  components: { VueHcaptcha },
  methods: {
    onVerify (token) {
      this.token = token
    },
    register() {
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = { name: this.name, email: this.email, password: this.password , password2: this.password2, captcha: this.token}
      axios.post('/register', payload)
        .then(() => {
          this.verify = true
        })
        .catch((error) => {
          EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
          this.$refs.captcha.reset()
        })
        .finally(() => this.loading = false)
    },
  }
}
</script>