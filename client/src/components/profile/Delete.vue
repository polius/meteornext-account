<template>
  <div>
    <div class="text-h6 font-weight-medium">Delete account</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">Please note, deleting your account is a permanent action and will no be recoverable once completed.</div>
    <v-checkbox v-model="confirm" color="red" label="I confirm I want to delete my Meteor Next account." style="margin-top:15px" hide-details>
      <template v-slot:label>
        <div style="margin-left:5px">
          <div style="color:black">I confirm I want to delete my Meteor Next account.</div>
          <div class="font-weight-regular caption" style="color:black; font-size:0.85rem !important">Existing active licenses will be canceled.</div>
        </div>
      </template>
    </v-checkbox>
    <v-btn :loading="loading" color="#e74c3c" @click="submitDelete" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Delete account</v-btn>
  </div>
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