<template>
  <div>
    <div class="text-h6 font-weight-medium">Change license</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">Upgrade your license by selecting the amount of servers you want to have per user.</div>
    <v-card style="background:transparent">
      <v-card-text>
        <v-form ref="form" @submit.prevent>
          <p class="text-h6 font-weight-regular" style="color:black; font-size:1.8rem!important; margin-top:10px; margin-bottom:15px">{{ price == 0 ? 'Free' : '$' + price }}<span v-if="price != 0" class="text-h6 font-weight-light" style="color:black; font-size:1.4rem!important; margin-left:5px">/ Month</span></p>
          <div class="text-body-1 font-weight-regular" style="color:black; margin-bottom:5px">How many servers?</div>
          <v-select solo :loading="loading" v-model="license" :items="account.pricing" item-value="units" item-text="units" class="text-body-1" style="max-width:170px" hide-details>
            <template v-slot:[`selection`]="{ item }">
              <span v-if="item.units == -1" style="color:black">Unlimited</span>
              <span v-else>{{ item.units + (item.units == 1 ? ' server' : ' servers')}}</span>
            </template>
            <template v-slot:[`item`]="{ item }">
              <span v-if="item.units == -1" style="color:black">Unlimited</span>
              <span v-else>{{ item.units + (item.units == 1 ? ' server' : ' servers')}}</span>
            </template>
          </v-select>
          <div v-if="license > 1" class="text-body-1 font-weight-regular" style="color:black; margin-top:15px">{{ `Avg. $${average} per server` }}</div>
        </v-form>
      </v-card-text>
    </v-card>
    <v-btn :loading="loading" color="#2c7be5" @click="submitChange" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px;">Change license</v-btn>
  </div>
</template>

<script>
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    loading: false,
    license: null,
  }),
  props: {
    enabled: Boolean,
    account: Object
  },
  computed: {
    dialog: {
      get() { return this.enabled },
      set(value) { this.$emit('update', value) },
    },
    resources() {
      if (this.account === undefined || this.account.license === undefined) return ''
      return this.account.license.resources
    },
    price() {
      if (this.account === undefined || this.account.license === undefined) return ''
      if (this.license != null) return this.account.pricing.filter(x => x.units == this.license)[0]['price']
      return this.account.pricing.filter(x => x.units == this.resources)[0]['price']
    },
    validLicense() {
      if (this.license == null || parseInt(this.license) != this.license || this.license == this.resources) return false
      return true
    },
    average() {
      if (this.account === undefined || this.account.license === undefined) return ''
      if (this.license == null) return (this.account.pricing.filter(x => x.units == this.resources)[0]['price'] / this.license).toFixed(1)
      return (this.account.pricing.filter(x => x.units == this.license)[0]['price'] / this.license).toFixed(1)
    }
  },
  methods: {
    submitChange() {
      this.loading = true
      const payload = { 'resources': this.license }
      axios.post('/account/change', payload)
        .then((response) => {
          this.dialog = false
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
          EventBus.$emit('get-account')
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
  },
  watch: {
    resources(val) {
      if (val != '') this.license = val
    },
  },
}
</script>