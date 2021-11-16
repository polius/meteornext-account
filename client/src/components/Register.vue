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
                  <div class="display-2" style="color:black; margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline" style="font-size:1.3rem!important; color:black; margin-top:10px; margin-bottom:20px">ACCOUNT | REGISTER</div>
                  <v-divider></v-divider>
                  <div v-if="validate" style="margin-top:20px; margin-bottom:5px">
                    <v-icon style="color:#3cbab3; margin-left:auto; margin-right:auto">fas fa-envelope-open-text</v-icon>
                    <div class="text-h6" style="color:black">Validate your account</div>
                    <div class="text-body-1 font-weight-light" style="color:black; margin-top:14px">We have sent an email to the address you entered</div>
                    <div @click="resend" class="text-body-2 font-weight-medium" style="cursor:pointer; color:#1976d2; margin-top:16px">Resend validation email</div>
                  </div>
                  <v-form v-else ref="form" @submit.prevent style="margin-top:20px">
                    <v-text-field ref="name" filled v-model="name" label="Full Name" :rules="[v => !!v || '']" required v-on:keyup.enter="register()" style="margin-bottom:20px;" hide-details autofocus></v-text-field>
                    <v-text-field ref="email" filled v-model="email" name="email" label="Email" :rules="emailRules" required v-on:keyup.enter="register()" style="margin-bottom:20px;" hide-details></v-text-field>
                    <v-text-field ref="password" filled v-model="password" name="password" label="Password" :rules="[v => !!v || '']" required type="password" v-on:keyup.enter="register()" style="margin-bottom:20px;" hide-details></v-text-field>
                    <v-btn x-large type="submit" color="info" :loading="loading" block style="margin-top:0px;" @click="register()">CREATE ACCOUNT</v-btn>
                    <div class="text-body-2" style="color:black; margin-top:15px">Have an account? <router-link to="/login" style="text-decoration:none; font-weight:500">Sign in</router-link></div>
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

<script>
import axios from 'axios'
import EventBus from '../js/event-bus'

export default {
  data: () => ({
    loading: false,
    emailRules: [
      v => !!v || 'E-mail is required',
      v => /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(v) || 'E-mail must be valid',
    ],
    name: '',
    email: '',
    password: '',
    validate: false,
  }),
  methods: {
    register() {
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = { name: this.name, email: this.email, password: this.password }
      axios.post('/register', payload)
        .then((response) => {
          this.validate = true
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
        })
        .catch((error) => {
          EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
    resend() {
      axios.post('/resend', payload)
        .then((response) => {
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
        })
        .catch((error) => {
          EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
    },
  }
}
</script>