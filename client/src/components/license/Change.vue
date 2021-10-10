<template>
  <v-dialog v-model="dialog" max-width="512px">
    <v-card>
      <v-toolbar dense flat color="primary">
        <v-toolbar-title class="white--text subtitle-1">CHANGE LICENSE</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false" icon><v-icon style="font-size:22px">fas fa-times-circle</v-icon></v-btn>
      </v-toolbar>
      <v-card-text style="padding:15px">
        <v-container style="padding:0px">
          <v-layout wrap>
            <v-flex xs12>
              <v-form ref="form" @submit.prevent>
                <p class="text-h6 font-weight-regular white--text" style="font-size:1.8rem!important; text-align:center; margin-top:10px; margin-bottom:10px">{{ price == 0 ? 'Free' : '$' + price }}<span v-if="price != 0" class="text-h6 font-weight-light white--text" style="font-size:1.4rem!important; margin-left:5px">/ Month</span></p>
                <div class="text-body-1 font-weight-regular" style="font-size:1.1rem !important; text-align:center; margin-bottom:15px">How many servers?</div>
                <v-select outlined v-model="license" :items="account.pricing" item-value="units" item-text="units" class="text-body-1 white--text" style="margin-left:auto; margin-right:auto; max-width:150px" hide-details>
                  <template v-slot:[`selection`]="{ item }">
                    <span v-if="item.units == -1">Unlimited</span>
                    <span v-else>{{ item.units + (item.units == 1 ? ' server' : ' servers')}}</span>
                  </template>
                  <template v-slot:[`item`]="{ item }">
                    <span v-if="item.units == -1">Unlimited</span>
                    <span v-else>{{ item.units + (item.units == 1 ? ' server' : ' servers')}}</span>
                  </template>
                </v-select>
                <div v-if="license > 1" class="text-body-1 font-weight-regular white--text" style="text-align:center; margin-top:15px; margin-bottom:5px">{{ `Avg. $${average} per server` }}</div>
              </v-form>
              <v-divider style="margin-top:20px"></v-divider>
              <v-row no-gutters style="margin-top:15px">
                <v-btn :disabled="!validLicense" :loading="loading" color="#00b16a" @click="submitChange">CONFIRM</v-btn>
                <v-btn :disabled="loading" color="#EF5354" @click="dialog = false" style="margin-left:5px">CANCEL</v-btn>
                <v-spacer/>
                <v-btn text :disabled="loading" color="white" @click="dialog = false" style="margin-left:5px">{{ $vuetify.breakpoint.smAndDown ? 'INFO' : 'INFORMATION' }}</v-btn>
              </v-row>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
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
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      return this.account.license.resources
    },
    price() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      if (this.license != null) return this.account.pricing.filter(x => x.units == this.license)[0]['price']
      return this.account.pricing.filter(x => x.units == this.resources)[0]['price']
    },
    validLicense() {
      if (this.license == null || parseInt(this.license) != this.license || this.license == this.resources) return false
      return true
    },
    average() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      if (this.license == null) return (this.account.pricing.filter(x => x.units == this.resources)[0]['price'] / this.license).toFixed(1)
      return (this.account.pricing.filter(x => x.units == this.license)[0]['price'] / this.license).toFixed(1)
    }
  },
  methods: {
    submitChange() {
      this.loading = true
      axios.post('/account/change')
        .then((response) => {
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
    dialog: function(val) {
      if (val) {
        this.license = this.resources
        requestAnimationFrame(() => {
          if (typeof this.$refs.form !== 'undefined') this.$refs.form.resetValidation()
          // if (typeof this.$refs.form !== 'undefined') this.$refs.passwordCurrent.focus()
        })
      }
    }
  },
}
</script>