<template>
  <div style="height:100%">
    <v-main :style="{ height:'100%', padding:'0px', backgroundImage: 'url(' + require('@/assets/bg.jpg') + ')', backgroundRepeat: 'no-repeat', backgroundSize: 'cover' }">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <v-card style="border-radius:5px; background-color:#444444">
                <v-card-text>
                  <v-avatar :size="130" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                  <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | REGISTER</div>
                  <v-divider></v-divider>
                  <div v-if="verify" style="margin-top:20px; margin-bottom:5px">
                    <div class="text-h6 white--text" style="font-weight:400">Verify your email</div>
                    <div class="text-body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px; color:#e2e2e2">We have sent an email to the address you entered</div>
                  </div>
                  <v-form v-else ref="form" @submit.prevent style="margin-top:20px">
                    <v-text-field ref="email" filled v-model="email" name="email" label="Email" :rules="emailRules" required style="margin-bottom:20px;" hide-details autofocus></v-text-field>
                    <v-text-field ref="password" filled v-model="password" name="password" label="Password" :rules="[v => !!v || '']" required type="password" style="margin-bottom:20px;" hide-details></v-text-field>
                    <v-text-field ref="password2" filled v-model="password2" name="password2" label="Confirm Password" :rules="[v => !!v || '']" required type="password" style="margin-bottom:20px;" hide-details></v-text-field>
                    <vue-hcaptcha ref="captcha" data-theme="dark" sitekey="d4fcdf7d-363a-495b-8e51-aff6e138aa6c" @verify="onVerify"></vue-hcaptcha>
                    <v-btn x-large type="submit" color="info" :loading="loading" block style="margin-top:10px;" @click="register()">CREATE ACCOUNT</v-btn>
                    <div class="text-body-2" style="margin-top:15px; color:#e2e2e2">Have an account? <router-link to="/login" style="text-decoration:none; font-weight:500">Sign in</router-link></div>
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
::v-deep .v-main::before {
  content: "";
  position: absolute;
  top: 0px;
  right: 0px;
  bottom: 0px;
  left: 0px;
  background-color: rgba(0,0,0,0.05);
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
      v => !!v || 'E-mail is required',
      v => /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(v) || 'E-mail must be valid',
    ],
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
      const payload = { email: this.email, password: this.password , password2: this.password2, captcha: this.token}
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