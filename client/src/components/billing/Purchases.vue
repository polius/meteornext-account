<template>
  <div>
    <div class="text-h6 font-weight-medium">Purchase history</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">See your purchases history and download any related invoice.</div>
    <v-text-field v-model="search" placeholder="Search" style="padding-top:0px" hide-details></v-text-field>
    <v-card style="margin-top:15px; background-color:transparent">
      <v-data-table :loading="account.billing === undefined" :headers="headers" :items="items" :search="search" :options="{itemsPerPage: 3}" :footer-props="{'items-per-page-options':[3, 6, 12, -1]}" :hide-default-footer="items.length == 0" no-data-text="No payments done" style="background-color:transparent">
        <template v-slot:[`item.created_date`]="{ item }">
          {{ dateFormat(item.created_date) }}
        </template>
        <template v-slot:[`item.resources`]="{ item }">
          {{ item.resources == -1 ? 'Unlimited' : item.resources }}
        </template>
        <template v-slot:[`item.price`]="{ item }">
          {{ `€ ${priceFormat(item.price)}` }}
        </template>
        <template v-slot:[`item.status`]="{ item }">
          <v-icon :color="item.status == 'paid' ? '#20bf6b' : '#EF5354'" small style="margin-bottom:2px; margin-right:5px">{{ item.status == 'paid' ? 'fas fa-check-circle' : 'fas fa-times-circle'}}</v-icon>
          {{ item.status == 'paid' ? 'Payment successful' : item.status == 'unpaid' ? 'Payment failed' : 'Payment expired' }}
        </template>
        <template v-slot:[`item.invoice_url`]="{ item }">
          <v-btn v-if="item.invoice_url != null" icon title="View invoice details"><v-icon small @click="viewInvoice(item.invoice_url)">fas fa-external-link-alt</v-icon></v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<style scoped>
div {
  cursor:default !important;
}
</style>

<script>
import moment from 'moment'

export default {
  data: () => ({
    loading: false,
    headers: [
      { text: 'Purchase date', value: 'created_date' },
      { text: 'Resources', value: 'resources' },
      { text: 'Price', value: 'price' },
      { text: 'Status', value: 'status' },
      { text: 'Invoice', value: 'invoice_url'},
    ],
    search: '',
  }),
  props: {
    account: Object
  },
  computed: {
    items() {
      if (this.account.billing === undefined) return []
      return this.account.billing.invoices
    }
  },
  methods: {
    viewInvoice(invoice_url) {
      window.open(invoice_url, '_blank')
    },
    dateFormat(date) {
      if (date) return moment.utc(date).local().format("DD MMMM YYYY, HH:mm:ss")
      return date
    },
    priceFormat(price) {
      let newPrice = price.toString()
      if (newPrice.split('.').length > 1 && newPrice.split('.')[1].length === 1) newPrice += '0'
      return newPrice
    },
  }
}
</script>
