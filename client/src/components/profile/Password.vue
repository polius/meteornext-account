<template>
  <v-dialog v-model="dialog" max-width="640px">
    <v-card>
      <v-toolbar dense flat color="primary">
        <v-toolbar-title class="white--text subtitle-1">CHANGE PASSWORD</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false" icon><v-icon style="font-size:22px">fas fa-times-circle</v-icon></v-btn>
      </v-toolbar>
      <v-card-text style="padding:15px">
        <v-container style="padding:0px">
          <v-layout wrap>
            <v-flex xs12>
              <v-form ref="passwordForm" @submit.prevent>
                <v-text-field ref="passwordCurrent" v-model="item.current" :readonly="loading" label="Current password" type="password" :rules="[v => !!v || '']" required style="padding-top:10px" autocomplete="new-password" v-on:keyup.enter="submitPassword"></v-text-field>
                <v-text-field v-model="item.new" :readonly="loading" label="New password" type="password" :rules="[v => !!v || '']" required style="padding-top:0px" autocomplete="new-password" v-on:keyup.enter="submitPassword"></v-text-field>
                <v-text-field v-model="item.repeat" :readonly="loading" label="Repeat new password" type="password" :rules="[v => !!v || '']" required style="padding-top:0px" autocomplete="new-password" v-on:keyup.enter="submitPassword"></v-text-field>
              </v-form>
              <v-divider></v-divider>
              <v-row no-gutters style="margin-top:20px;">
                <v-btn :loading="loading" color="#00b16a" @click="submitPassword">CONFIRM</v-btn>
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
    item: { current: '', new: '', repeat: '' }
  }),
  props: {
    enabled: Boolean
  },
  computed: {
    dialog: {
      get() { return this.enabled },
      set(value) { this.$emit('update', value) },
    }
  },
  methods: {
    submitPassword() {
      // Check if all fields are filled
      if (!this.$refs.passwordForm.validate()) {
        EventBus.$emit('send-notification', 'Please make sure all required fields are filled out correctly', '#EF5354')
        return
      }
      this.loading = true
      const payload = this.item
      axios.put('/account/password', payload)
        .then((response) => {
          this.dialog = false
          EventBus.$emit('send-notification', response.data.message, '#00b16a')
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
        this.item = { current: '', new: '', repeat: ''}
        requestAnimationFrame(() => {
          if (typeof this.$refs.passwordForm !== 'undefined') this.$refs.passwordForm.resetValidation()
          if (typeof this.$refs.passwordCurrent !== 'undefined') this.$refs.passwordCurrent.focus()
        })
      }
    }
  },
}
</script>