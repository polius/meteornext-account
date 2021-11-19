<template>
  <v-card>
    <v-toolbar flat dense color="primary">
      <v-toolbar-title class="white--text subtitle-1"><v-icon small style="margin-right:10px; margin-bottom:3px">fas fa-coins</v-icon>BILLING</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <div v-show="!$vuetify.breakpoint.smAndDown">
        <v-row no-gutters>
          <v-col cols="auto">
            <v-btn :disabled="loading" style="margin-right:10px">Change Payment Method</v-btn>
          </v-col>
            <v-btn :disabled="loading" style="margin-right:10px">Export Billings</v-btn>
          <v-col cols="auto">
          </v-col>
          <v-col style="margin-left:10px">
            <v-text-field v-model="search" placeholder="Search billings" style="padding-top:0px" hide-details></v-text-field>
          </v-col>
        </v-row>
      </div>
      <div v-show="$vuetify.breakpoint.smAndDown">
        <v-btn block :disabled="loading" style="margin-right:10px">Change Payment Method</v-btn>
        <v-btn block :disabled="loading" style="margin-right:10px; margin-top:15px">Export Billings</v-btn>
        <v-text-field solo v-model="search" placeholder="Search billings" background-color="#303030" style="margin-top:15px; margin-bottom:15px" hide-details></v-text-field>
      </div>
      <v-card style="margin-top:15px">
        <v-data-table :headers="headers" :items="items" :search="search" :options="{itemsPerPage: 3}" :footer-props="{'items-per-page-options':[3, 6, 12, -1]}">
          <template v-slot:[`item.status`]="{ item }">
            <v-icon :color="item.status == 'success' ? '#20bf6b' : item.status == 'pending' ? '#ff9800' : '#EF5354'" small style="margin-bottom:2px; margin-right:5px">fas fa-circle</v-icon>
            {{ item.status.charAt(0).toUpperCase() + item.status.slice(1) }}
          </template>
        </v-data-table>
      </v-card>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'Billing',
  data: () => ({
    loading: false,
    headers: [
      { text: 'Purchase Date', value: 'date' },
      { text: 'Servers', value: 'servers' },
      { text: 'Price', value: 'price' },
      { text: 'Status', value: 'status' },
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
}
</script>
