<template>
  <div v-if="!valid" style="height:100%">
    <v-main style="height:100%">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <div>
                <div @click="goBack" style="text-align:center; margin-bottom:5px; font-size:16px; font-weight:400; cursor:pointer!important; width:80px; background-color:rgba(61, 61, 80, 0.5); padding:10px; border-radius:5px">
                  <v-icon size="15" style="margin-right:8px; padding-bottom:3px">fas fa-arrow-left</v-icon>Back
                </div>
                <v-card style="border-radius:5px; background-color:rgba(61, 61, 80, 0.8)">
                  <v-card-text>
                    <v-avatar :size="100" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                    <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                    <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | Verify Email</div>
                    <v-divider></v-divider>
                    <div style="margin-top:20px; margin-bottom:10px">
                      <v-icon size="40" color="#f0ad4e" style="margin-right:10px">fas fa-exclamation-triangle</v-icon>
                      <p style="color:white; font-size:19px; margin-top:25px; margin-bottom:25px">This link has expired</p>
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
div {
  cursor:default !important;
}
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
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    valid: true
  }),
  created() {
    if (this.$route.params.code === undefined) EventBus.$emit('send-notification', 'Invalid Code', '#EF5354')
    else {
      const payload = { code: this.$route.params.code }
      axios.post('/account/email/verify', payload)
      .then(() => this.$router.push({name: 'login', params: {status: 'emailVerified'}}))
      .catch(() => this.valid = false)
    }
  },
  methods: {
    goBack() {
      this.$router.push('/login')
    },
  }
}
</script>