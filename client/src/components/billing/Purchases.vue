<template>
  <div>
    <div class="text-h6 font-weight-medium">Purchase history</div>
    <div class="body-1 font-weight-light" style="margin-top:15px; margin-bottom:15px">See your purchases history and download any related invoice.</div>
    <v-text-field v-model="search" placeholder="Search" style="padding-top:0px" hide-details></v-text-field>
    <v-card style="margin-top:15px">
      <v-data-table :headers="headers" :items="items" :search="search" :options="{itemsPerPage: 3}" :footer-props="{'items-per-page-options':[3, 6, 12, -1]}">
        <template v-slot:[`item.status`]="{ item }">
          <v-icon :color="item.status == 'success' ? '#20bf6b' : item.status == 'pending' ? '#ff9800' : '#EF5354'" small style="margin-bottom:2px; margin-right:5px">fas fa-circle</v-icon>
          {{ item.status.charAt(0).toUpperCase() + item.status.slice(1) }}
        </template>
        <template v-slot:[`item.invoice`]="{ item }">
          <v-btn icon title="Download invoice"><v-icon small @click="downloadInvoice(item)">fas fa-arrow-down</v-icon></v-btn>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
export default {
  data: () => ({
    loading: false,
    headers: [
      { text: 'Date', value: 'date' },
      { text: 'Resources', value: 'servers' },
      { text: 'Price', value: 'price' },
      { text: 'Status', value: 'status' },
      { text: 'Invoice', value: 'invoice'},
    ],
    items: [
      { date: '2021-10-01 12:00:00', servers: '25', price: '57.5€', status: 'pending'},
      { date: '2021-09-01 12:00:00', servers: '10', price: '24€', status: 'success'},
      { date: '2021-08-01 12:00:00', servers: '10', price: '24€', status: 'failed'},
      { date: '2021-07-01 12:00:00', servers: '5', price: '12.5€', status: 'success'},
      { date: '2021-06-01 12:00:00', servers: '5', price: '12.5€', status: 'success'},
    ],
    search: '',
  }),
  props: {
    account: Object
  },
}
</script>
