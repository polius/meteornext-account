<template>
  <v-dialog v-model="dialog" max-width="645px">
    <v-card>
      <v-toolbar dense flat color="primary">
        <v-toolbar-title class="white--text subtitle-1">DELETE ACCOUNT</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false" icon><v-icon style="font-size:22px">fas fa-times-circle</v-icon></v-btn>
      </v-toolbar>
      <v-card-text style="padding:15px">
        <v-container style="padding:0px">
          <v-layout wrap>
            <v-flex xs12>
              <v-form ref="form" @submit.prevent>
                <v-alert colored-border elevation="2">
                  <v-icon color="#ff9900" style="margin-bottom:2px; margin-right:10px; font-size:20px">fas fa-exclamation-triangle</v-icon>Caution! This action is non-reversible.
                </v-alert>
                <div class="body-1">Are you sure you want to proceed with the deletion of your Meteor Next account?</div>
                <v-checkbox v-model="confirm" label="I confirm I want to delete my Meteor Next account.">
                  <template v-slot:label>
                    <div style="margin-left:5px">
                      <div class="white--text">I confirm I want to delete my Meteor Next account.</div>
                      <div class="font-weight-regular caption" style="font-size:0.85rem !important">Existing active licenses will be canceled.</div>
                    </div>
                  </template>
                </v-checkbox>
              </v-form>
              <v-divider></v-divider>
              <v-row no-gutters style="margin-top:20px;">
                <v-btn :disabled="!confirm" :loading="loading" color="#00b16a" @click="submitDelete">CONFIRM</v-btn>
                <v-btn :disabled="loading" color="#EF5354" @click="dialog = false" style="margin-left:5px">CANCEL</v-btn>
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
    confirm: false,
    loading: false,
  }),
  props: {
    enabled: Boolean,
  },
  computed: {
    dialog: {
      get() { return this.enabled },
      set(value) { this.$emit('update', value) },
    }
  },
  methods: {
    submitDelete() {
      this.loading = true
      axios.delete('/account')
        .then((response) => {
          this.dialog = false
          this.$store.dispatch('app/logout').then(() => {
            EventBus.$emit('send-notification', response.data.message,'#00b16a')
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
  watch: {
    dialog: function(val) {
      if (val) {
        this.confirm = false
      }
    }
  },
}
</script>