<template>
  <v-dialog v-model="dialog" max-width="640px">
    <v-card>
      <v-toolbar dense flat color="primary">
        <v-toolbar-title class="white--text subtitle-1">CHANGE EMAIL</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false" icon><v-icon style="font-size:22px">fas fa-times-circle</v-icon></v-btn>
      </v-toolbar>
      <v-card-text style="padding:15px">
        <v-container style="padding:0px">
          <v-layout wrap>
            <v-flex xs12>
              <v-form ref="form" @submit.prevent>
                <v-text-field v-model="email" readonly label="Current email" style="padding-top:5px"></v-text-field>
                <v-text-field v-on:keyup.enter="submitEmail()" ref="email" v-model="item" :readonly="loading" label="New email" :rules="[v => !!v || '', v => /.+@.+\..+/.test(v) || '']" required style="padding-top:0px"></v-text-field>
              </v-form>
              <v-divider></v-divider>
              <v-row no-gutters style="margin-top:20px;">
                <v-btn :loading="loading" color="#00b16a" @click="submitEmail">CONFIRM</v-btn>
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
    loading: false,
    item: '',
  }),
  props: {
    enabled: Boolean,
    email: String
  },
  computed: {
    dialog: {
      get() { return this.enabled },
      set(value) { this.$emit('update', value) },
    }
  },
  methods: {
    submitEmail() {
      // Check if all fields are filled
      if (!this.$refs.form.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = { 'email': this.item }
      axios.put('/account/email', payload)
        .then((response) => {
          this.dialog = false
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
        this.item = ''
        requestAnimationFrame(() => {
          if (typeof this.$refs.form !== 'undefined') this.$refs.form.resetValidation()
          if (typeof this.$refs.email !== 'undefined') this.$refs.email.focus()
        })
      }
    }
  },
}
</script>