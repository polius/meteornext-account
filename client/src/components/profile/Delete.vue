<template>
  <div>
    <div class="text-h6 font-weight-medium">Delete account</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">Please note, deleting your account is a permanent action and will no be recoverable once completed.</div>
    <v-checkbox v-model="confirm" color="red" label="I confirm I want to delete my Meteor Next account." style="margin-top:15px" hide-details>
      <template v-slot:label>
        <div style="margin-left:5px">
          <div style="color:#e2e2e2">I confirm I want to delete my Meteor Next account.</div>
          <div class="font-weight-regular caption" style="font-size:0.85rem !important">Existing active licenses will be canceled. The data stored in your database will not be deleted.</div>
        </div>
      </template>
    </v-checkbox>
    <v-btn :loading="loading" color="#eb4d4b" @click="deleteAccount" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Delete account</v-btn>
    <v-dialog v-model="dialog" width="640px">
      <v-card>
        <v-toolbar dense flat color="rgb(50, 50, 60)" style="border:solid rgba(255, 255, 255, 0.12) 1px">
          <v-toolbar-title class="white--text text-body-1 font-weight-regular">Delete account</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:15px; background-color:rgb(65, 65, 75); border:solid rgba(255, 255, 255, 0.12) 1px; border-top:0px">
          <v-card style="background-color:rgb(60, 60, 70)">
            <v-row no-gutters align="center" justify="center">
              <v-col cols="auto" style="display:flex; margin:15px">
                <v-icon size="18" color="warning">fas fa-exclamation-triangle</v-icon>
              </v-col>
              <v-col>
                <div class="text-body-1" style="color:#e2e2e2">This action cannot be undone</div>
              </v-col>
            </v-row>
          </v-card>
          <v-card style="margin-top:12px; background-color:rgb(60, 60, 70)">
            <v-row no-gutters align="center" justify="center">
              <v-col cols="auto" style="display:flex; margin:15px">
                <v-icon color="#eb4d4b" size="20">fas fa-exclamation-circle</v-icon>
              </v-col>
              <v-col>
                <div class="text-body-1" style="color:#e2e2e2">Your account will be automatically deleted</div>
              </v-col>
            </v-row>
          </v-card>
          <div class="text-body-1" style="margin-top:15px">Are you sure you want to delete your account?</div>
          <v-divider style="margin-top:15px"></v-divider>
          <v-row no-gutters style="margin-top:15px;">
            <v-btn :loading="loading" color="primary" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitDelete">Confirm</v-btn>
            <v-btn :disabled="loading" text color="white" @click="dialog = false" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import EventBus from '../../js/event-bus'

export default {
  data: () => ({
    confirm: false,
    loading: false,
    dialog: false,
  }),
  methods: {
    deleteAccount() {
      if (!this.confirm) EventBus.$emit('send-notification', 'Please confirm you want to delete your account.', '#EF5354')
      else this.dialog = true
    },
    submitDelete() {
      this.loading = true
      axios.delete('/account')
        .then((response) => {
          this.dialog = false
          this.$store.dispatch('app/logout').then(() => {
            EventBus.$emit('send-notification', response.data.message,'#20bf6b')
            this.$router.push('/login')
          })
        })
        .catch((error) => {
          if ([401,422,503].includes(error.response.status)) this.$store.dispatch('app/logout').then(() => this.$router.push('/login'))
          else EventBus.$emit('send-notification', error.response.data.message !== undefined ? error.response.data.message : 'Internal Server Error', '#EF5354')
        })
        .finally(() => this.loading = false)
    },
  },
}
</script>