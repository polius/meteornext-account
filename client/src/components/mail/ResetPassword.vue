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
                  <div class="headline" style="font-size:1.3rem!important; color:black; margin-top:10px; margin-bottom:20px">ACCOUNT | Reset Password</div>
                  <v-divider></v-divider>
                  <div v-if="$route.params.code === undefined">
                    <div v-if="!completed">
                      <v-form ref="form" @submit.prevent>
                        <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left">Email</div>
                        <v-text-field flat v-model="item.email" :readonly="loading" :rules="emailRules" solo v-on:keyup.enter="submitEmail()" style="padding-top:5px" hide-details autofocus></v-text-field>
                      </v-form>
                      <v-btn block x-large :loading="loading" color="info" @click="submitEmail" style="margin-top:20px">SUBMIT</v-btn>
                    </div>
                    <div v-else style="margin-top:20px; margin-bottom:10px">
                      <div class="text-h6" style="color:black; font-weight:400">Verify your email</div>
                      <div class="text-body-1 font-weight-light" style="color:black; margin-top:15px; margin-bottom:15px">We have sent an email to the address you entered</div>
                      </div>
                    </div>
                  <div v-else>
                    <div v-if="valid != null && valid" style="margin-top:20px; margin-bottom:10px">
                      <v-form ref="form" @submit.prevent>
                        <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left">New password</div>
                        <v-text-field flat v-model="item.password" :readonly="loading" type="password" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" autofocus hide-details></v-text-field>
                        <div class="text-body-2 font-weight-medium" style="margin-top:15px; text-align:left">Confirm new password</div>
                        <v-text-field flat v-model="item.password2" type="password" :readonly="loading" :rules="[v => !!v || '']" solo style="padding-top:5px" autocomplete="new-password" hide-details></v-text-field>
                      </v-form>
                      <v-btn block x-large :loading="loading" color="info" @click="submitPassword" style="margin-top:20px">RESET PASSWORD</v-btn>
                    </div>
                    <div v-else-if="valid != null && !valid" style="margin-top:20px; margin-bottom:10px">
                      <div class="text-body-1 font-weight-medium" style="color:black;">ERROR</div>
                      <div class="text-body-1" style="color:black; margin-top:5px">This link has expired</div>
                    </div>
                  </div>
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
::v-deep .v-input--is-focused .v-input__control {
  border: 1px solid #2196f3 !important; /* #005fcc */
}
::v-deep .v-input__control {
  border: 1px solid #d2ddec !important;
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
        .then(() => this.$router.push('/login'))
        .catch((error) => {
          EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
  }
}
</script>