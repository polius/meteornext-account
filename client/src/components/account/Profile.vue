<template>
  <div>
    <v-card style="height:100%">
      <v-toolbar flat dense color="primary">
        <v-toolbar-title class="white--text subtitle-1"><v-icon small style="margin-right:10px; margin-bottom:3px">fas fa-user</v-icon>PROFILE</v-toolbar-title>
      </v-toolbar>
      <v-card-text style="padding: 20px 20px 20px;">
        <v-container fluid grid-list-lg style="padding:0px">
          <v-layout row wrap>
            <v-flex xs12>
              <v-text-field readonly v-model="account.email" :loading="loading" :disabled="loading" label="Email" style="padding-top:5px"></v-text-field>
              <v-text-field readonly v-model="account.creation_date" :loading="loading" :disabled="loading" label="Creation Date" style="padding-top:0px" hide-details></v-text-field>
              <v-btn :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Change Email</v-btn>
              <v-btn @click="passwordDialog = true" :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Change Password</v-btn>
              <v-btn :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Manage MFA</v-btn>
              <v-btn :block="$vuetify.breakpoint.smAndDown" :disabled="loading" color="#EF5354" style="margin-top:15px" outlined>Delete Account</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
    <v-dialog v-model="passwordDialog" max-width="640px">
      <v-card>
        <v-toolbar dense flat color="primary">
          <v-toolbar-title class="white--text subtitle-1">CHANGE PASSWORD</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn @click="passwordDialog = false" icon><v-icon style="font-size:22px">fas fa-times-circle</v-icon></v-btn>
        </v-toolbar>
        <v-card-text style="padding:15px">
          <v-container style="padding:0px">
            <v-layout wrap>
              <v-flex xs12>
                <v-form ref="passwordForm" @submit.prevent>
                  <v-text-field ref="passwordCurrent" v-model="passwordItem.current" :readonly="loadingDialog" label="Current password" type="password" :rules="[v => !!v || '']" required style="padding-top:5px" autocomplete="new-password"></v-text-field>
                  <v-text-field v-model="passwordItem.new" :readonly="loadingDialog" label="New password" type="password" :rules="[v => !!v || '']" required style="padding-top:0px" autocomplete="new-password"></v-text-field>
                  <v-text-field v-model="passwordItem.repeat" :readonly="loadingDialog" label="Repeat new password" type="password" :rules="[v => !!v || '']" required style="padding-top:0px" autocomplete="new-password" v-on:keyup.enter="submitPassword"></v-text-field>
                </v-form>
                <v-divider></v-divider>
                <v-row no-gutters style="margin-top:20px;">
                  <v-btn :loading="loadingDialog" color="#00b16a" @click="submitPassword">CONFIRM</v-btn>
                  <v-btn :disabled="loadingDialog" color="#EF5354" @click="passwordDialog = false" style="margin-left:5px">CANCEL</v-btn>
                </v-row>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Profile',
  data: () => ({
    loading: false,
    account: { email: 'pol.alzina@gmail.com', creation_date: '2021-10-01 12:00:00'},
    // Password Dialog
    loadingDialog: false,
    passwordDialog: false,
    passwordItem: { current: '', new: '', repeat: '' }
  }),
  methods: {
    submitPassword() {
      // Check if all fields are filled
      if (!this.$refs.passwordForm.validate()) {
        this.notification('Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loadingDialog = true
      const payload = this.passwordItem
      axios.put('/account/password', payload)
        .then((response) => {
          this.passwordDialog = false
          this.notification(response.data.message, '#00b16a')
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else this.notification(error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loadingDialog = false)
    },
  },
  watch: {
    passwordDialog: function(val) {
      if (val) {
        this.passwordItem = { current: '', new: '', repeat: ''}
        requestAnimationFrame(() => {
          if (typeof this.$refs.passwordForm !== 'undefined') this.$refs.passwordForm.resetValidation()
          if (typeof this.$refs.passwordCurrent !== 'undefined') this.$refs.passwordCurrent.focus()
        })
      }
    }
  },
}
</script>
