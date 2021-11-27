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
                  <div class="headline" style="font-size:1.3rem!important; color:black; margin-top:10px; margin-bottom:20px">ACCOUNT | Update Payment</div>
                  <v-divider></v-divider>
                  <div v-if="valid == null" class="text-center" style="margin-top:20px; margin-bottom:10px">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                  </div>
                  <div v-else-if="valid == false" style="margin-top:20px; margin-bottom:10px">
                    <div class="text-body-1 font-weight-medium" style="color:black;">ERROR</div>
                    <div class="text-body-1" style="color:black; margin-top:5px">This link has expired</div>
                  </div>
                  <div v-else-if="valid == true" style="margin-top:20px; margin-bottom:10px">
                    <div class="text-h6" style="color:black">Payment information changed</div>
                    <v-row no-gutters>
                      <v-col>
                        <v-icon size="50" color="#20bf6b" style="margin:15px">fas fa-check-circle</v-icon>
                      </v-col>
                    </v-row>
                    <v-btn @click="goAccount" color="info" style="margin-top:10px">Go to Account</v-btn>
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

<script>
import axios from 'axios'

export default {
  data: () => ({
    valid: null
  }),
  created() {
    if (this.$route.params.code === undefined) this.valid = false
    else if (this.$route.params.code == 'ok') this.valid = true
    else {
      const payload = { code: this.$route.params.code }
      axios.post('/account/billing/update', payload)
      .then((response) => window.location.href = response.data.url)
      .catch(() => this.valid = false)
    }
  },
  methods: {
    goAccount() {
      this.$router.push('/billing')
    },
  },
}
</script>