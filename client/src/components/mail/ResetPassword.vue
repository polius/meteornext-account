<template>
  <div style="height:100%">
    <v-main style="height:100%">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <div>
                <div @click="goBack" style="text-align:center; margin-bottom:5px; color:#183153; font-size:16px; font-weight:400; cursor:pointer; width:80px; background-color:rgba(61, 61, 80, 0.05); padding:10px; border-radius:5px">
                  <v-icon size="15" style="margin-right:8px; padding-bottom:3px; color:#183153">fas fa-arrow-left</v-icon>Back
                </div>
                <v-card style="border-radius:5px; background-color:rgba(61, 61, 80, 0.8)">
                  <v-card-text>
                    <v-avatar :size="100" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                    <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                    <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | Reset Password</div>
                    <v-divider></v-divider>
                    <div v-if="$route.params.code === undefined">
                      <div v-if="!completed">
                        <v-form ref="form" @submit.prevent>
                          <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">Email</div>
                          <v-text-field flat v-model="item.email" type="email" :readonly="loading" :rules="emailRules" solo v-on:keyup.enter="submitEmail()" style="padding-top:5px" hide-details autofocus></v-text-field>
                        </v-form>
                        <v-btn block x-large :loading="loading" color="info" @click="submitEmail" style="margin-top:20px">SUBMIT</v-btn>
                      </div>
                      <div v-else style="margin-top:20px; margin-bottom:10px">
                        <div class="text-h6 white--text" style="font-weight:400">Verify your email</div>
                        <div class="text-body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px; color:white">We have sent an email to the address you entered</div>
                        </div>
                      </div>
                    <div v-else>
                      <div v-if="valid != null && valid" style="margin-top:20px; margin-bottom:10px">
                        <v-form ref="form" @submit.prevent>
                          <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">New password</div>
                          <v-text-field flat v-model="item.password" :readonly="loading" type="password" :rules="[v => !!v || '']" v-on:keyup.enter="submitPassword" solo style="padding-top:5px" autocomplete="new-password" hint="Use 8 or more characters with a mix of letters and numbers" persistent-hint autofocus></v-text-field>
                          <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left; color:white">Confirm new password</div>
                          <v-text-field flat v-model="item.password2" type="password" :readonly="loading" :rules="[v => !!v || '']" v-on:keyup.enter="submitPassword" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
                        </v-form>
                        <v-btn block x-large :loading="loading" color="info" @click="submitPassword" style="margin-top:20px">RESET PASSWORD</v-btn>
                      </div>
                      <div v-else-if="valid != null && !valid" style="margin-top:20px; margin-bottom:10px">
                        <v-icon size="40" color="#f0ad4e" style="margin-right:10px">fas fa-exclamation-triangle</v-icon>
                        <p style="color:white; font-size:19px; margin-top:25px; margin-bottom:25px">This link has expired</p>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </div>
            </v-slide-y-transition>
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
  </div>
</template>

<style scoped>
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
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    completed: false,
    valid: null,
    loading: false,
    item: { email: '', password: '', password2: '' },
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(v) || 'E-mail must be valid',
    ],
  }),
  created() {
    if (this.$route.params.code !== undefined) this.checkCode()
  },
  methods: {
    submitEmail() {
      // Check if all fields are filled
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = { email: this.item.email }
        axios.post('/account/password/reset', payload)
        .then(() => this.completed = true)
        .catch((error) => {
          EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    checkCode() {
      const payload = { code: this.$route.params.code }
      axios.get('/account/password/reset', { params: payload })
        .then(() => this.valid = true)
        .catch(() => this.valid = false)
    },
    submitPassword() {
      // Check if all fields are filled
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = { code: this.$route.params.code, password: this.item.password, password2: this.item.password2 }
        axios.post('/account/password/reset', payload)
        .then(() => this.$router.push({name: 'login', params: {status: 'passwordUpdated'}}))
        .catch((error) => {
          EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    goBack() {
      this.$router.push('/login')
    },
  }
}
</script>