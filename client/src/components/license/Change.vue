<template>
  <div style="height:100%">
    <v-main style="height:100%">
      <v-container grid-list-xl text-center style="height:100%; display:flex; justify-content:center; align-items:center;">
        <v-layout row wrap align-center style="max-width:800px;">
          <v-flex>
            <v-slide-y-transition mode="out-in">
              <div>
                <div @click="goBack" style="text-align:center; margin-bottom:5px; font-size:16px; font-weight:400; cursor:pointer!important; width:80px; background-color:rgba(61, 61, 80, 0.5); padding:10px; border-radius:5px">
                  <v-icon size="15" style="margin-right:8px; padding-bottom:3px">fas fa-arrow-left</v-icon>Back
                </div>
                <v-card style="border-radius:5px; background-color:rgba(61, 61, 80, 0.75)">
                  <v-card-text>
                    <v-avatar :size="100" style="margin-top:10px;"><img src="https://meteornext.io/assets/logo.png" /></v-avatar>
                    <div class="display-2 white--text" style="margin-top:10px;"><span style="font-weight:500">Meteor</span> Next</div>
                    <div class="headline white--text" style="font-size:1.3rem!important; margin-top:10px; margin-bottom:20px">ACCOUNT | CHANGE LICENSE</div>
                    <v-divider></v-divider>
                    <div v-if="init" style="height:255px; display:flex; justify-content:center; align-items:center">
                      <v-progress-circular indeterminate></v-progress-circular>
                    </div>
                    <div v-else-if="$route.params.id !== undefined && $route.params.id == 'success'" style="margin-top:20px">
                      <p style="color:white; font-size:19px; margin-top:30px; margin-bottom:30px"><v-icon size="22" color="#20bf6b" style="margin-right:10px; padding-bottom:3px">fas fa-check-circle</v-icon>License successfully changed</p>
                      <div class="text-body-1" style="color:#f6f6f6; margin-top:15px; margin-bottom:15px"><v-icon size="20" color="orange" style="margin-right:10px; padding-bottom:4px">fas fa-star</v-icon>Don't forget to <span style="color:white; font-weight: 500">REFRESH</span> the license in your app to update the number of resources.</div>
                      <v-img @click="overlay = !overlay" src="https://docs.meteornext.io/assets/admin-settings-license.4343a336.png" style="margin-bottom:10px; border-radius:5px"></v-img>
                      <v-overlay :value="overlay" style="width:100%; padding:12px">
                        <v-btn large @click="overlay = false" style="margin-bottom:20px"><v-icon style="margin-right:10px; font-size:15px; padding-bottom:1px">fas fa-times</v-icon>Close</v-btn>
                        <v-img src="https://docs.meteornext.io/assets/admin-settings-license.4343a336.png" style="border-radius:5px; max-width:1500px; margin:auto"></v-img>
                      </v-overlay>
                      <v-btn @click="goBack" color="info" style="margin-top:10px">Go To Account</v-btn>
                    </div>
                    <div v-else style="margin-top:20px">
                      <div v-if="license == null" class="text-center" style="margin-bottom:10px">
                        <v-progress-circular indeterminate color="primary"></v-progress-circular>
                      </div>
                      <v-form v-else ref="form" @submit.prevent>
                        <p class="text-h6 font-weight-regular white--text" style="font-size:2rem!important; margin-top:20px; margin-bottom:20px">
                          <span style="font-size:24px; vertical-align:middle; margin-right:5px; padding-bottom:2px">{{ license.priceInteger == 0 ? '' : license.priceCurrency }}</span>
                          <span>{{ license.priceInteger == 0 ? 'Free' : license.priceInteger }}</span>
                          <span style="font-size:20px">{{ license.priceInteger == 0 ? '' : license.priceDecimal }}</span>
                          <span v-if="license.priceInteger != 0" class="text-h6 font-weight-light" style="color:#e2e2e2; font-size:20px!important; margin-left:5px">/ Month</span>
                        </p>
                        <div class="text-body-1 font-weight-regular" style="color:white">Enter the amount of servers</div>
                        <v-text-field :readonly="resourcesText == 'Unlimited'" @keypress="isNumber($event)" @input="calculatePrice" solo v-model="resourcesText" class="centered-input" style="width:120px; margin-left:auto; margin-right:auto; margin-top:15px; margin-bottom:6px" hide-details></v-text-field>
                        <v-slider @input="calculatePrice" :readonly="loading" v-model="resourcesSlider" min="1" max="500" style="margin-left:50px; margin-right:50px" hide-details></v-slider>
                        <div v-if="resourcesText != 'Unlimited'" class="text-body-1 font-weight-regular" style="color:#e2e2e2">{{ `Avg. ${license.priceAverage}€ per server` }}</div>
                        <v-btn block x-large :disabled="(resourcesText == license.resources) || (resourcesText == 'Unlimited' && license.resources == -1)" :loading="loading" color="info" @click="submitChange(false)" style="margin-top:20px">CHANGE LICENSE</v-btn>
                      </v-form>
                    </div>
                  </v-card-text>
                </v-card>
              </div>
            </v-slide-y-transition>
          </v-flex>
        </v-layout>
      </v-container>
    </v-main>
    <v-dialog v-model="dialog" width="640px">
      <v-card style="background-color:#fffcfa">
        <v-toolbar dense flat color="rgb(50, 50, 60)">
          <v-toolbar-title class="white--text text-body-1 font-weight-regular">Change license</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:15px; background-color:rgb(65, 65, 75); border:solid rgba(255, 255, 255, 0.12) 1px">
          <v-card style="background-color:rgb(60, 60, 70)">
            <v-row no-gutters align="center" justify="center">
              <v-col cols="auto" style="display:flex; margin:15px">
                <v-icon size="20" color="warning">fas fa-exclamation-triangle</v-icon>
              </v-col>
              <v-col>
                <div class="text-body-1" style="color:#e2e2e2">This action cannot be undone.</div>
              </v-col>
            </v-row>
          </v-card>
          <v-card style="margin-top:15px; background-color:rgb(60, 60, 70)">
            <v-row no-gutters align="center" justify="center">
              <v-col cols="auto" style="display:flex; margin:15px">
                <v-icon color="#eb4d4b" size="20">fas fa-exclamation-circle</v-icon>
              </v-col>
              <v-col>
                <div class="text-body-1" style="color:#e2e2e2">Active subscriptions will automatically be cancelled.</div>
              </v-col>
            </v-row>
          </v-card>
          <div class="text-body-1" style="margin-top:15px">Are you sure you want to change your license to <span class="font-weight-medium">1 Server</span>?</div>
          <v-divider style="margin-top:15px"></v-divider>
          <v-row no-gutters style="margin-top:15px;">
            <v-btn :loading="loading" color="primary" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitChange(true)">Confirm</v-btn>
            <v-btn :disabled="loading" text color="white" @click="dialog = false" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped>
div {
  cursor:default !important;
}
::v-deep .centered-input .v-input__control {
  border: 1px solid rgba(61, 61, 80, 0.2) !important;
}
::v-deep .centered-input .v-input__control .v-input__slot {
  background-color:rgba(61, 61, 80, 0.3) !important;
}
::v-deep .centered-input input {
  text-align: center;
}
::v-deep .v-responsive__content {
  cursor: pointer;
}
::v-deep .v-overlay__content {
  width: 100%;
}
</style>

<script>
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    init: true,
    loading: false,
    dialog: false,
    license: {
      resources: 1,
      priceCurrency: '€',
      priceInteger: 0,
      priceDecimal: 0,
      priceAvg: null
    },
    resourcesText: 1,
    resourcesSlider: 1,
    overlay: false,
  }),
  created() {
    this.getLicense()
  },
  methods: {
    getLicense() {
      this.loading = true
      axios.get('/license')
        .then((response) => {
          const license = response.data.license
          this.license.resources = license.resources
          this.calculatePrice(license.resources, license.price)
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => { this.loading = false; this.init = false })
    },
    submitChange(confirm) {
      if (this.resourcesText == 1 && !confirm) this.dialog = true
      else {
        this.loading = true
        const payload = { 'resources': this.resourcesText }
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
    isNumber(event) {
      const keysAllowed = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
      const keyPressed = event.key
      if (!keysAllowed.includes(keyPressed) || this.resourcesSlider == 500) event.preventDefault()
    },
    calculatePrice(resources, price) {
      if (resources.length == 0) return

      // Init pricing
      const max_price_x_server = 10
      const max_price_reduction = 8.5
      const max_servers = 500
      
      // Check resources parameter
      resources = Number.isNaN(parseInt(resources)) ? this.license.resources : parseInt(resources)
      resources = (resources == 0) ? 1 : resources

      if (price !== undefined) {
        this.license.priceInteger = Math.trunc(price)
        this.license.priceDecimal = ('.' + Math.trunc((price - Math.trunc(price)) * 100) + '0').substring(0,3)
        this.priceAverage = parseFloat(price / resources).toFixed(2)
      }
      if (resources == -1) {
        // Modify UI resources
        setTimeout(() => {
          this.resourcesText = 'Unlimited'
          this.resourcesSlider = max_servers
        },0)
      }
      else if (resources == 1) {
        this.license.priceInteger = 0
        this.license.priceDecimal = 0
        this.license.priceAverage = 0

        // Modify UI resources
        setTimeout(() => {
          this.resourcesText = resources
          this.resourcesSlider = resources
        },0)
      }
      else if (resources > 1) {
        // Calculate Servers Count
        if (resources > max_servers) resources = max_servers

        // Calculate Servers Pricing
        let price_x_server = max_price_x_server
        if (resources < 5) price_x_server = max_price_x_server
        else if (resources > 5) price_x_server = max_price_x_server - (((max_price_x_server - max_price_reduction) / max_servers) * resources)
        const new_price = (resources < 5) ? 5 * max_price_x_server : price_x_server * resources

        // Assign components values
        this.license.priceInteger = Math.trunc(new_price)
        this.license.priceDecimal = ('.' + Math.trunc((new_price - Math.trunc(new_price)) * 100) + '0').substring(0,3)
        this.license.priceAverage = parseFloat(price_x_server).toFixed(2)
        
        // Modify UI resources
        setTimeout(() => {
          this.resourcesText = resources
          this.resourcesSlider = resources
        },0)
      }
    },
    goBack() {
      this.$router.push('/')
    },
  },
}
</script>