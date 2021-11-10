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
                  <div class="headline" style="font-size:1.3rem!important; color:rgba(255,255,255,.9); margin-top:10px; margin-bottom:20px">ACCOUNT | REGISTER</div>
                  <v-divider></v-divider>
                  <v-form ref="form" @submit.prevent style="margin-top:20px">
                    <v-text-field ref="name" filled v-model="name" label="Full Name" :rules="[v => !!v || '']" required v-on:keyup.enter="register()" style="margin-bottom:20px;" hide-details autofocus></v-text-field>
                    <v-text-field ref="email" filled v-model="email" name="email" label="Email" :rules="emailRules" required v-on:keyup.enter="register()" style="margin-bottom:20px;" hide-details></v-text-field>
                    <v-text-field ref="password" filled v-model="password" name="password" label="Password" :rules="[v => !!v || '']" required type="password" v-on:keyup.enter="register()" style="margin-bottom:20px;" hide-details></v-text-field>
                  </v-form>
                  <v-btn x-large type="submit" color="info" :loading="loading" block style="margin-top:0px;" @click="register()">CREATE ACCOUNT</v-btn>
                  <div class="text-body-2 white--text" style="margin-top:15px">Have an account? <router-link to="/login" style="text-decoration:none; font-weight:500">Sign in</router-link></div>
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
  }),
  methods: {
    register() {
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      
    },
  }
}
</script>