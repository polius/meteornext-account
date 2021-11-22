<template>
  <div>
    <div class="text-h6 font-weight-medium">Cancel subscription</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">After cancelling your subscription, your current license will not be renewed and when it expires, it will be changed automatically to 1 Resource / user.</div>
    <v-btn :loading="loading" color="#eb4d4b" @click="dialog = true" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:20px">Cancel subscription</v-btn>
    <v-dialog v-model="dialog" max-width="672px">
      <v-card style="background-color:#fffcfa">
        <v-toolbar dense flat color="#f5983b">
          <v-toolbar-title class="white--text text-body-1 font-weight-medium">Cancel subscription</v-toolbar-title>
        </v-toolbar>
        <v-card-text style="padding:15px">
          <div class="text-body-1" style="color:black">Are you sure you want to cancel your subscription?</div>
          <v-divider style="margin-top:15px"></v-divider>
          <v-row no-gutters style="margin-top:15px;">
            <v-btn :loading="loading" color="#20bf6b" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white" @click="submitCancel">Confirm</v-btn>
            <v-btn :disabled="loading" color="#eb4d4b" @click="dialog = false" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-left:5px">Cancel</v-btn>
          </v-row>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
  data: () => ({
    loading: false,
    dialog:false
  }),
  props: {
    account: Object
  },
  methods: {
    submitCancel() {

    },
  },
}
</script>
