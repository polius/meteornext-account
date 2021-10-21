<template>
  <div>
    <v-card style="height:100%">
      <v-toolbar flat dense color="primary">
        <v-toolbar-title class="white--text subtitle-1"><v-icon small style="margin-right:10px; margin-bottom:3px">fas fa-certificate</v-icon>LICENSE</v-toolbar-title>
      </v-toolbar>
      <v-card-text style="padding: 20px 20px 20px;">
        <v-container fluid grid-list-lg style="padding:0px">
          <v-layout row wrap>
            <v-flex xs12>
              <v-text-field readonly v-model="resources" :loading="loading" :disabled="loading" label="Resources" style="padding-top:5px"></v-text-field>
              <v-text-field readonly v-model="pricing" :loading="loading" :disabled="loading" label="Pricing" style="padding-top:0px"></v-text-field>
              <v-text-field readonly v-model="expiration" :loading="loading" :disabled="loading" label="Expiration Date" style="padding-top:0px" hide-details></v-text-field>
              <v-btn @click="keysDialog = true" :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Show License Key</v-btn>
              <v-btn @click="changeDialog = true" :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Change License</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
    <Key :enabled="keysDialog" :account="account" @update="keysDialog = $event"/>
    <Change :enabled="changeDialog" :account="account" @update="changeDialog = $event"/>
  </div>
</template>

<script>
import Key from './Key'
import Change from './Change'

export default {
  name: 'License',
  data: () => ({
    keysDialog: false,
    changeDialog: false
  }),
  props: {
    loading: Boolean,
    account: Object
  },
  components: { Key, Change },
  computed: {
    resources() {
      if (this.loading || this.account === undefined) return ''
      if (this.account.license.resources == -1) return 'Unlimited'
      return this.account.license.resources + (this.account.license.resources == 1 ? ' Server' : ' Servers')
    },
    pricing() {
      if (this.loading || this.account === undefined) return ''
      if (this.account.license.resources == 1) return 'Free'
      return '$' + this.account.pricing.filter(x => x.units == this.account.license.resources)[0]['price'] + ' / Month'
    },
    expiration() {
      if (this.loading || this.account === undefined) return ''
      if (this.account.license.expiration) return this.account.license.expiration_date
      return 'Lifetime'
    },
  },
}
</script>
