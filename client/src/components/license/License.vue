<template>
  <div>
    <Summary :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Key :account="account"/>
  </div>
</template>

<script>
import Summary from './Summary'
import Key from './Key'

export default {
data: () => ({
  }),
  props: {
    account: Object
  },
  components: { Summary, Key },
}
</script>
