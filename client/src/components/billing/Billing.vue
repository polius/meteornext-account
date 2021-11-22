<template>
  <div>
    <Summary :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Purchases :account="account"/>
  </div>
</template>

<script>
import Summary from './Summary'
import Purchases from './Purchases'

export default {
  data: () => ({
  }),
  components: { Summary, Purchases },
  props: {
    account: Object
  },
}
</script>
