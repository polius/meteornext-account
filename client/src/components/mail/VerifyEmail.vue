<template>
  <div v-if="!valid" style="height:100%">
    <v-main style="height:'100%'">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <div>
                <div @click="goBack" style="text-align:left; margin-bottom:5px; color:#f6f6f6; font-size:17px; font-weight:400; cursor:pointer; width:56px">
                  <v-icon size="15" style="margin-right:5px; padding-bottom:3px">fas fa-arrow-left</v-icon>Back
                </div>
                <v-card style="border-radius:5px; background-color:rgba(61, 61, 80, 0.7)">
                  <v-card-text>
                    <v-avatar :size="100" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                    <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                    <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | Verify Email</div>
                    <v-divider></v-divider>
                    <div style="margin-top:20px; margin-bottom:10px">
                      <div class="text-body-1 font-weight-medium">ERROR</div>
                      <div class="text-body-1" style="margin-top:5px">This link has expired</div>
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
      .then(() => this.$router.push('/login'))
      .catch(() => this.valid = false)
    }
  },
  method: {
    goBack() {
      this.$router.push('/')
    },
  }
}
</script>