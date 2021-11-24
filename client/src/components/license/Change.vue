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
                  <div class="headline" style="font-size:1.3rem!important; color:black; margin-top:10px; margin-bottom:20px">ACCOUNT | CHANGE LICENSE</div>
                  <v-divider></v-divider>
                  <div v-if="$route.params.id !== undefined && $route.params.id == 'success'" style="margin-top:20px">
                    <div class="text-h6" style="color:black">License successfully changed</div>
                    <v-icon size="50" color="#20bf6b" style="margin:15px">fas fa-check-circle</v-icon>
                    <div class="text-body-1" style="color:black">Thanks for your purchase :)</div>
                    <v-btn @click="goBack" color="info" style="margin-top:15px">Go back</v-btn>
                  </div>
                  <div v-else style="margin-top:20px">
                    <div v-if="license == null" class="text-center" style="margin-bottom:10px">
                      <v-progress-circular indeterminate color="primary"></v-progress-circular>
                    </div>
                    <v-form v-else ref="form" @submit.prevent>
                      <p class="text-h6 font-weight-regular" style="color:black; font-size:1.8rem!important; margin-top:20px; margin-bottom:20px">{{ price == 0 ? 'Free' : '$' + price }}<span v-if="price != 0" class="text-h6 font-weight-light" style="color:black; font-size:1.4rem!important; margin-left:5px">/ Month</span></p>
                      <div class="text-body-1 font-weight-regular" style="color:black">How many
                      <v-tooltip right>
                        <template v-slot:activator="{ on }">
                          <span v-on="on" class="text-body-1" style="border-bottom: 1px solid #ddd">resources</span>
                        </template>
                        <span>1 Resource = 1 Server / User</span>
                      </v-tooltip>?</div>
                      <v-select solo :readonly="loading" v-model="newLicense" :items="products" item-value="resources" item-text="resources" class="text-body-1" style="max-width:180px; margin-top:10px; margin-left:auto; margin-right:auto" hide-details>
                        <template v-slot:[`selection`]="{ item }">
                          <span v-if="item.resources == -1" style="color:black">Unlimited</span>
                          <span v-else>{{ item.resources + (item.resources == 1 ? ' resource' : ' resources')}}</span>
                        </template>
                        <template v-slot:[`item`]="{ item }">
                          <span v-if="item.resources == -1" style="color:black">Unlimited</span>
                          <span v-else>{{ item.resources + (item.resources == 1 ? ' resource' : ' resources')}}</span>
                        </template>
                      </v-select>
                      <div v-if="newLicense > 1" class="text-body-1 font-weight-regular" style="color:black; margin-top:15px">{{ `Avg. $${average} per resource` }}</div>
                      <v-btn block x-large :disabled="!validLicense" :loading="loading" color="info" @click="submitChange" style="margin-top:20px">CHANGE LICENSE</v-btn>
                    </v-form>
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
    license: null,
    products: [],
    newLicense: null,
    loading: false,
  }),
  created() {
    if (this.$route.params.id === undefined) this.getLicense()
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
    submitChange() {
      // Check if user selected 1 Resource. Open dialog for confirmation. 1 resource does not need Stripe checkout.
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
    },
    goBack() {
      this.$router.push('/')
    },
  },
}
</script>