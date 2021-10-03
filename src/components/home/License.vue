<template>
  <v-card dark color="#424242">
    <v-toolbar flat dense color="#2196f3 !important">
      <v-toolbar-title class="white--text subtitle-1"><v-icon small style="margin-right:10px; margin-bottom:3px">fas fa-certificate</v-icon>LICENSE</v-toolbar-title>
    </v-toolbar>
    <v-card-text style="padding: 20px 20px 20px;">
      <v-container fluid grid-list-lg style="padding:0px">
        <v-layout row wrap>
          <v-flex xs12>
            <v-text-field readonly v-model="license.current" :loading="loading" :disabled="loading" label="Current License" style="padding-top:5px"></v-text-field>
            <v-text-field readonly v-model="license.pricing" :loading="loading" :disabled="loading" label="Pricing" style="padding-top:0px"></v-text-field>
            <v-text-field readonly v-model="license.expiration" :loading="loading" :disabled="loading" label="Expiration Date" style="padding-top:0px" hide-details></v-text-field>
            <v-btn :block="$vuetify.breakpoint.mdAndDown" :disabled="loading" color="#424242" style="margin-right:10px; margin-top:15px">Change License</v-btn>
            <!-- <v-btn :block="$vuetify.breakpoint.mdAndDown" :disabled="loading" color="#424242" style="margin-top:15px">Download Meteor</v-btn> -->
          </v-flex>
        </v-layout>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'License',
  data: () => ({
    loading: false,
    license: { current: '1 Server', pricing: 'Free', expiration: 'Lifetime' }
  }),
}
</script>
