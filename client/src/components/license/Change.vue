<template>
  <div style="height:100%">
    <v-main :style="{ height:'100%', padding:'0px', backgroundImage: 'url(' + require('@/assets/bg.jpg') + ')', backgroundRepeat: 'no-repeat', backgroundSize: 'cover' }">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:500px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <v-card style="border-radius:5px; background-color:#444444">
                <v-card-text>
                  <v-avatar :size="100" style="margin-top:10px;"><img :src="require('@/assets/logo.png')" /></v-avatar>
                  <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                  <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | CHANGE LICENSE</div>
                  <v-divider></v-divider>
                  <div v-if="$route.params.id !== undefined && $route.params.id == 'success'" style="margin-top:20px">
                    <div class="text-h6">License successfully changed</div>
                    <v-row no-gutters>
                      <v-col>
                        <v-icon size="50" color="#20bf6b" style="margin:15px">fas fa-check-circle</v-icon>
                      </v-col>
                    </v-row>
                    <div v-if="license != null && license.resources > 1" class="text-body-1" style="margin-bottom:10px">Thanks for your purchase :)</div>
                    <v-btn @click="goBack" color="info" style="margin-top:10px">Go back</v-btn>
                  </div>
                  <div v-else style="margin-top:20px">
                    <div v-if="license == null" class="text-center" style="margin-bottom:10px">
                      <v-progress-circular indeterminate color="primary"></v-progress-circular>
                    </div>
                    <v-form v-else ref="form" @submit.prevent>
                      <p class="text-h6 font-weight-regular white--text" style="font-size:1.8rem!important; margin-top:20px; margin-bottom:20px">{{ price == 0 ? 'Free' : '$' + price }}<span v-if="price != 0" class="text-h6 font-weight-light" style="color:#e2e2e2; font-size:1.4rem!important; margin-left:5px">/ Month</span></p>
                      <div class="text-body-1 font-weight-regular" style="color:#e2e2e2">Enter the amount of servers</div>
                      <v-text-field solo v-model="newLicense" class="centered-input" style="width:200px; margin-left:auto; margin-right:auto; margin-top:15px; margin-bottom:6px" hide-details></v-text-field>
                      <v-slider :readonly="loading" v-model="newLicense" min="5" max="1000" style="margin-left:50px; margin-right:50px" hide-details></v-slider>
                      <!-- <v-select solo :readonly="loading" v-model="newLicense" :items="products" item-value="resources" item-text="resources" class="text-body-1" style="max-width:180px; margin-top:10px; margin-left:auto; margin-right:auto" hide-details>
                        <template v-slot:[`selection`]="{ item }">
                          <span v-if="item.resources == -1">Unlimited</span>
                          <span v-else>{{ item.resources + (item.resources == 1 ? ' resource' : ' resources')}}</span>
                        </template>
                        <template v-slot:[`item`]="{ item }">
                          <span v-if="item.resources == -1">Unlimited</span>
                          <span v-else>{{ item.resources + (item.resources == 1 ? ' resource' : ' resources')}}</span>
                        </template>
                      </v-select> -->
                      <div v-if="newLicense > 1" class="text-body-1 font-weight-regular" style="color:#e2e2e2">{{ `Avg. $${average} per server` }}</div>
                      <v-btn block x-large :disabled="!validLicense" :loading="loading" color="info" @click="submitChange(false)" style="margin-top:20px">CHANGE LICENSE</v-btn>
                    </v-form>
                  </div>
                </v-card-text>
              </v-card>
            </v-slide-y-transition>
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
    <v-dialog v-model="dialog" width="640px">
      <v-card style="background-color:#fffcfa">
        <v-toolbar dense flat color="#f5983b">
          <v-toolbar-title class="white--text text-body-1 font-weight-medium">Change license</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:15px">
          <v-card>
            <v-row no-gutters align="center" justify="center">
              <v-col cols="auto" style="display:flex; margin:15px">
                <v-icon color="warning">fas fa-exclamation-triangle</v-icon>
              </v-col>
              <v-col>
                <div class="text-body-1">This action cannot be undone.</div>
              </v-col>
            </v-row>
          </v-card>
          <div class="text-body-1" style="margin-top:15px">Are you sure you want to change your license to <span class="font-weight-medium">1 Resource</span>?</div>
          <v-divider style="margin-top:15px"></v-divider>
          <v-row no-gutters style="margin-top:15px;">
            <v-btn :loading="loading" color="#20bf6b" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitChange(true)">Confirm</v-btn>
            <v-btn :disabled="loading" color="#eb4d4b" @click="dialog = false" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
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

::v-deep .centered-input input {
  text-align: center
}
</style>

<script>
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    license: null,
    products: [],
    newLicense: null,
    loading: false,
    dialog: false,
  }),
  created() {
    this.getLicense()
  },
  computed: {
    resources() {
      if (this.license == null) return ''
      return this.license.resources
    },
    price() {
      if (this.license == null) return ''
      return this.products.filter(x => x.resources == this.newLicense)[0]['price']
    },
    validLicense() {
      if (this.license == null || parseInt(this.newLicense) == this.license.resources) return false
      return true
    },
    average() {
      if (this.license == null) return ''
      return (this.products.filter(x => x.resources == this.newLicense)[0]['price'] / this.newLicense).toFixed(1)
    }
  },
  methods: {
    getLicense() {
      axios.get('/license')
        .then((response) => {
          this.license = response.data.license
          this.products = response.data.products
          this.newLicense = this.license.resources
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
    },
    submitChange(confirm) {
      if (this.newLicense == 1 && !confirm) this.dialog = true
      else {
        this.loading = true
        const payload = { 'resources': this.newLicense }
        axios.post('/license', payload)
          .then((response) => {
            window.location.href = response.data.url
          })
          .catch((error) => {
            if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
            else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
          })
          .finally(() => this.loading = false)
      }
    },
    calculatePrice() {
      
    },
    goBack() {
      this.$router.push('/')
    },
  },
}
</script>