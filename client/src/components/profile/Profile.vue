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
              <v-text-field readonly v-model="email" :loading="loading" :disabled="loading" label="Email" style="padding-top:5px"></v-text-field>
              <v-text-field readonly v-model="created_at" :loading="loading" :disabled="loading" label="Creation Date" style="padding-top:0px" hide-details></v-text-field>
              <v-btn @click="emailDialog = true" :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Change Email</v-btn>
              <v-btn @click="passwordDialog = true" :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Change Password</v-btn>
              <v-btn @click="mfaDialog = true" :block="$vuetify.breakpoint.smAndDown" :disabled="loading" style="margin-right:10px; margin-top:15px">Manage MFA</v-btn>
              <v-btn @click="deleteDialog = true" :block="$vuetify.breakpoint.smAndDown" :disabled="loading" color="#EF5354" style="margin-top:15px" outlined>Delete Account</v-btn>
            </v-flex>
          </v-layout>
        </v-container>
      </v-card-text>
    </v-card>
    <Password :enabled="passwordDialog" @update="passwordDialog = $event"/>
    <Email :enabled="emailDialog" :email="email" @update="emailDialog = $event"/>
    <MFA :enabled="mfaDialog" @update="mfaDialog = $event" mode="profile"/>
    <Delete :enabled="deleteDialog" @update="deleteDialog = $event"/>
  </div>
</template>

<script>
import moment from 'moment'

import Password from './Password'
import Email from './Email'
import MFA from '../mfa/MFA'
import Delete from './Delete'

export default {
  data: () => ({
    passwordDialog: false,
    emailDialog: false,
    mfaDialog: false,
    deleteDialog: false,
  }),
  components: { Password, Email, MFA, Delete },
  props: {
    loading: Boolean,
    account: Object
  },
  computed: {
    email() {
      return (this.loading || this.account === undefined) ? '' : this.account.profile.email
    },
    created_at() {
      return (this.loading || this.account === undefined) ? '' : this.dateFormat(this.account.profile.created_at)
    },
  },
  methods: {
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("YYYY-MM-DD HH:mm:ss")
      return date
    },
  }
}
</script>
