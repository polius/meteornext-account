<template>
    <div>
      <v-form ref="summaryForm" @submit.prevent>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">Name</div>
        <div class="font-weight-light" style="font-size:15px; margin-top:5px">We will use this name for when we send you emails. Should be the customer's full name.</div>
        <v-text-field flat v-model="item.name" solo :rules="[v => !!v || '']" style="padding-top:5px" hide-details required></v-text-field>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">Email</div>
        <div class="font-weight-light" style="font-size:15px; margin-top:5px">We will email you a confirmation when changing your email, so please expect that email after submitting.</div>
        <v-text-field flat v-model="item.email" :readonly="loading" solo :rules="emailRules" style="padding-top:5px" hide-details></v-text-field>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">Company name <span class="font-weight-light">(optional)</span></div>
        <div class="font-weight-light" style="font-size:15px; margin-top:5px">This field is mandatory if you want to enter the EU VAT number.</div>
        <v-text-field flat v-model="item.company_name" :readonly="loading" solo style="padding-top:5px" hide-details></v-text-field>
        <div class="text-body-2 font-weight-medium" style="margin-top:15px">EU VAT number <span class="font-weight-light">(optional)</span></div>
        <div class="font-weight-light" style="font-size:15px; margin-top:5px">Enter the EU VAT number of your company. Applicable for European companies. <a href="https://www.meteornext.io/vat-number" target="_blank" style="color:rgb(63, 165, 251); text-decoration:none; font-weight:400;">More information</a></div>
        <v-text-field flat v-model="item.vat_number" :readonly="loading" solo placeholder="e.g. EU123456789" :rules="[v => !v || item.company_name && !!v || '']" style="padding-top:5px" hide-details>
          <v-tooltip v-if="vat.status == 'pending'" top slot="append">
            <template v-slot:activator="{ on, attrs }">
              <v-icon size="20" color="orange" v-bind="attrs" v-on="on" style="cursor:default">fas fa-spinner</v-icon>
            </template>
            <span class="text-body-2">Validating VAT Number... It can take few minutes to finish.</span>
          </v-tooltip>
          <v-tooltip v-else-if="vat.status == 'verified'" top slot="append">
            <template v-slot:activator="{ on, attrs }">
              <v-icon size="20" color="#20bf6b" v-bind="attrs" v-on="on" style="cursor:default">fas fa-check-circle</v-icon>
            </template>
            <span class="text-body-2">VAT Number validated.</span>
          </v-tooltip>
          <v-tooltip v-else-if="['unverified','unavailable'].includes(vat.status)" top slot="append">
            <template v-slot:activator="{ on, attrs }">
              <v-icon size="20" color="#EF5354" v-bind="attrs" v-on="on" style="cursor:default">fas fa-times-circle</v-icon>
            </template>
            <span class="text-body-2">VAT Number unverified.</span>
          </v-tooltip>
        </v-text-field>
      </v-form>
      <v-card v-if="vat.status == 'verified'" style="background-color: transparent; padding:10px; margin-top:10px">
        <div style="color:#20bf6b; font-weight:500">Valid VAT number registered to:</div>
        <div style="font-weight:500; margin-top:8px">Name</div>
        <div style="margin-top:3px">{{ vat.verified_name }}</div>
        <div style="font-weight:500; margin-top:10px">Address</div>
        <div style="margin-top:3px">{{ vat.verified_address }}</div>
      </v-card>
      <v-btn :disabled="loading" :loading="loading" color="info" @click="submitSummary" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Save</v-btn>
    </div>
  </template>
  
  <style scoped>
  div {
    cursor:default !important;
  }
  ::v-deep .v-input--is-focused .v-input__control {
    border: 1px solid #2196f3 !important;
  }
  ::v-deep .v-input__control {
    border: 1px solid #b6b6b6 !important;
  }
  ::v-deep .v-input__slot {
    background-color:rgba(61, 61, 80, 0.75) !important;
  }
  ::v-deep .no-edit div div {
    cursor:default !important;
  }
  ::v-deep .no-edit div div input {
    cursor:default !important;
  }
  </style>
  
  <script>
  import axios from 'axios'
  import EventBus from '../../js/event-bus'
  
  export default {
    data: () => ({
      loading: true,
      item: { name: '', email: '', company_name: '', vat_number: '' },
      vat: { status: '', verified_address: '', verified_name: '' },
      emailRules: [
        v => !!v || 'E-mail is required',
        v => /^(([^<>()[\]\\.,;:\s@']+(\.[^<>()\\[\]\\.,;:\s@']+)*)|('.+'))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(v) || 'E-mail must be valid',
      ],
    }),
    props: {
      account: Object
    },
    watch: {
      account(data) {
        this.item = {
          name: data.profile.name,
          email: data.profile.email,
          company_name: data.profile.company_name ? data.profile.company_name : '',
          vat_number: data.profile.vat_number ? data.profile.vat_number : '',
        }
        this.vat = {
          status: data.profile.vat_status ? data.profile.vat_status : '',
          verified_address: data.profile.vat_verified_address ? data.profile.vat_verified_address : '',
          verified_name: data.profile.vat_verified_name ? data.profile.vat_verified_name : '',
        }
        this.loading = false
      }
    },
    mounted() {
      this.checkVatNumber()      
    },
    methods: {
      submitSummary() {
        if (!this.$refs.summaryForm.validate()) {
          EventBus.$emit('send-notification', 'Please fill out all required fields.', '#EF5354')
          return
        }
        this.loading = true
        const payload = this.item
        axios.post('/profile', payload)
          .then((response) => {
            EventBus.$emit('send-notification', response.data.message, '#20bf6b')
            if (this.item.vat_number.length > 0) this.vat['status'] = 'pending'
            else this.vat['status'] = ''
            this.checkVatNumber()
          })
          .catch((error) => {
            if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
            else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
          })
          .finally(() => this.loading = false)
      },
      checkVatNumber() {
        axios.get('/account')
        .then((response) => {
          this.vat = {
            status: response.data.profile.vat_status,
            verified_address: response.data.profile.vat_verified_address,
            verified_name: response.data.profile.vat_verified_name
          }
          if (this.vat.status == 'pending') setTimeout(this.checkVatNumber, 5000)
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
      },
    },
  }
  </script>