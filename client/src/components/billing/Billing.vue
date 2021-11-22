<template>
  <div>
    <Summary :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Purchases :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Cancel :account="account"/>
  </div>
</template>

<script>
import Summary from './Summary'
import Purchases from './Purchases'
import Cancel from './Cancel'

export default {
  data: () => ({
  }),
  components: { Summary, Purchases, Cancel },
  props: {
    account: Object
  },
}
</script>
