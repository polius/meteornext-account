<template>
  <div v-if="!valid" style="height:100%">
    <v-main :style="{ height:'100%', padding:'0px', backgroundImage: 'url(' + require('@/assets/bg.jpg') + ')', backgroundRepeat: 'no-repeat', backgroundSize: 'cover' }">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <v-card style="border-radius:5px">
                <v-card-text>
                  <v-avatar :size="130" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                  <div class="display-2" style="color:black; margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline" style="font-size:1.3rem!important; color:black; margin-top:10px; margin-bottom:20px">ACCOUNT | Verify Email</div>
                  <v-divider></v-divider>
                  <div style="margin-top:20px; margin-bottom:10px">
                    <div class="text-body-1 font-weight-medium" style="color:black;">ERROR</div>
                    <div class="text-body-1" style="color:black;">This link has expired</div>
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
  }
}
</script>