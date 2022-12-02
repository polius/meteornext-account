<template>
  <div style="height:100%">
    <v-main style="height:100%">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <div>
                <div @click="goBack" style="text-align:center; margin-bottom:5px; font-size:16px; font-weight:400; cursor:pointer; width:80px; background-color:rgba(61, 61, 80, 0.1); padding:10px; border-radius:5px">
                  <v-icon size="15" style="margin-right:8px; padding-bottom:3px">fas fa-arrow-left</v-icon>Back
                </div>
                <v-card style="border-radius:5px; background-color:rgba(61, 61, 80, 0.8)">
                  <v-card-text>
                    <v-avatar :size="100" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                    <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                    <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | Update Payment</div>
                    <v-divider></v-divider>
                    <div v-if="valid == null" class="text-center" style="margin-top:20px; margin-bottom:10px">
                      <v-progress-circular indeterminate color="primary"></v-progress-circular>
                    </div>
                    <div v-else-if="valid == false" style="margin-top:20px; margin-bottom:10px">
                      <v-icon size="35" color="#f0ad4e" style="margin-right:10px">fas fa-exclamation-triangle</v-icon>
                      <p style="color:white; font-size:19px; margin-top:25px; margin-bottom:25px">{{ error }}</p>
                    </div>
                    <div v-else-if="valid == true" style="margin-top:20px; margin-bottom:10px">
                      <v-icon size="35" color="#20bf6b" style="margin-right:10px">fas fa-check-circle</v-icon>
                      <p style="color:white; font-size:19px; margin-top:25px; margin-bottom:25px">Payment information changed</p>
                      <v-btn @click="goAccount" color="info" style="margin-top:10px">Go To Account</v-btn>
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

export default {
  data: () => ({
    valid: null,
    error: '',
  }),
  created() {
    if (this.$route.params.code === undefined) this.valid = false
    else if (this.$route.params.code == 'ok') this.valid = true
    else {
      const payload = { code: this.$route.params.code }
      axios.post('/account/billing/update', payload)
      .then((response) => window.location.href = response.data.url)
      .catch((error) => {
        this.valid = false
        this.error = error.response.data.message !== undefined ? error.response.data.message : 'This link has expired'
      })
    }
  },
  methods: {
    goAccount() {
      this.$router.push('/billing')
    },
    goBack() {
      this.$router.push('/')
    },
  },
}
</script>