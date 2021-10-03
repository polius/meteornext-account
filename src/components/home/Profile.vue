<template>
  <v-card dark color="#424242">
    <v-toolbar flat dense color="#2196f3 !important">
      <v-toolbar-title class="white--text subtitle-1"><v-icon small style="margin-right:10px; margin-bottom:3px">fas fa-user</v-icon>PROFILE</v-toolbar-title>
    </v-toolbar>
    <v-card-text style="padding: 20px 20px 20px;">
      <v-container fluid grid-list-lg style="padding:0px">
        <v-layout row wrap>
          <v-flex xs12>
            <v-text-field readonly v-model="account.email" :loading="loading" :disabled="loading" label="Email" style="padding-top:5px"></v-text-field>
            <v-text-field readonly v-model="account.creation_date" :loading="loading" :disabled="loading" label="Creation Date" style="padding-top:0px" hide-details></v-text-field>
            <v-btn :block="$vuetify.breakpoint.smAndDown" :disabled="loading" color="#424242" style="margin-right:10px; margin-top:15px">Change Email</v-btn>
            <v-btn :block="$vuetify.breakpoint.smAndDown" :disabled="loading" color="#424242" style="margin-right:10px; margin-top:15px">Change Password</v-btn>
            <v-btn :block="$vuetify.breakpoint.smAndDown" :disabled="loading" color="#424242" style="margin-right:10px; margin-top:15px">Manage MFA</v-btn>
            <v-btn :block="$vuetify.breakpoint.smAndDown" :disabled="loading" color="#424242" style="margin-top:15px">Delete Account</v-btn>
          </v-flex>
        </v-layout>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'Profile',
  data: () => ({
    loading: false,
    account: { email: 'pol.alzina@gmail.com', creation_date: '2021-10-01 12:00:00'}
  }),
}
</script>
