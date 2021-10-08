<template>
  <v-dialog v-model="dialog" max-width="640px">
    <v-card>
      <v-toolbar dense flat color="primary">
        <v-toolbar-title class="white--text subtitle-1">LICENSE KEY</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false" icon><v-icon style="font-size:22px">fas fa-times-circle</v-icon></v-btn>
      </v-toolbar>
      <v-card-text style="padding:15px">
        <v-container style="padding:0px">
          <v-layout wrap>
            <v-flex xs12>
              <v-form ref="form" @submit.prevent>
                <div class="body-1" style="margin-bottom:10px">Use the following credentials to register your copy of Meteor Next.</div>
                <v-text-field @focus="$event.target.select()" outlined v-model="email" readonly label="Email" style="padding-top:5px" hide-details></v-text-field>
                <v-text-field @focus="$event.target.select()" outlined v-model="key" readonly label="Key" style="margin-top:20px" hide-details></v-text-field>
                <div class="body-1 white--text" style="margin-top:15px; margin-bottom:15px"><v-icon :style="`font-size:18px; margin-right:10px; margin-bottom:3px; color:${in_use ? '#ff9800' : '#00b16a'}`">{{ in_use ? 'fas fa-lock' : 'fas fa-unlock' }}</v-icon>{{ in_use ? 'License registered.' : 'License ready to be registered.' }}</div>
              </v-form>
              <v-divider></v-divider>
              <v-row no-gutters style="margin-top:20px;">
                <v-btn color="primary" @click="dialog = false">CLOSE</v-btn>
                <v-spacer/>
                <v-btn @click="submitUnregister" text :disabled="!in_use" :loading="loading">UNREGISTER LICENSE</v-btn>
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
    item: '',
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
    email() {
      if (this.loading || this.account === undefined || this.account.profile === undefined) return ''
      else return this.account.profile.email
    },
    key() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.key
    },
    in_use() {
      if (this.loading || this.account === undefined || this.account.license === undefined) return ''
      else return this.account.license.in_use
    }
  },
  methods: {
    submitUnregister() {
      // this.loading = true
      axios.post('/account/unregister')
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
}
</script>