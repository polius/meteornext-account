<template>
  <div>
    <div class="text-h6 font-weight-medium">Purchase history</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">See your purchases history and download any related invoice.</div>
    <v-text-field v-model="search" placeholder="Search" style="padding-top:0px" hide-details></v-text-field>
    <v-card style="margin-top:15px">
      <v-data-table :headers="headers" :items="items" :search="search" :options="{itemsPerPage: 3}" :footer-props="{'items-per-page-options':[3, 6, 12, -1]}" :hide-default-footer="items.length == 0" no-data-text="No payments done">
        <template v-slot:[`item.date`]="{ item }">
          {{ dateFormat(item.date) }}
        </template>
        <template v-slot:[`item.resources`]="{ item }">
          {{ item.resources == -1 ? 'Unlimited' : item.resources }}
        </template>
        <template v-slot:[`item.price`]="{ item }">
          {{ `$ ${item.price / 100}` }}
        </template>
        <template v-slot:[`item.status`]="{ item }">
          <v-icon :color="item.status == 'success' ? '#20bf6b' : item.status == 'pending' ? '#ff9800' : '#EF5354'" small style="margin-bottom:2px; margin-right:5px">fas fa-circle</v-icon>
          {{ item.status.charAt(0).toUpperCase() + item.status.slice(1) }}
        </template>
        <template v-slot:[`item.invoice`]="{ item }">
          <v-btn icon title="Download invoice"><v-icon small @click="downloadInvoice(item.invoice)">fas fa-arrow-down</v-icon></v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import moment from 'moment'

export default {
  data: () => ({
    loading: false,
    headers: [
      { text: 'ID', value: 'invoice_id' },
      { text: 'Purchase date', value: 'date' },
      { text: 'Resources', value: 'resources' },
      { text: 'Price', value: 'price' },
      { text: 'Status', value: 'status' },
      { text: 'Invoice', value: 'invoice'},
    ],
    search: '',
  }),
  props: {
    account: Object
  },
  computed: {
    items() {
      if (this.account.billing === undefined) return []
      return this.account.billing.payments
    }
  },
  methods: {
    downloadInvoice(invoice) {
      window.open(invoice, '_blank')
    },
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("DD MMMM YYYY HH:mm:ss")
      return date
    },
  }
}
</script>
