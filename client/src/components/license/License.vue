<template>
  <div style="margin:10px">
    <Summary :loading="loading" :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Key :loading="loading" :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Change :loading="loading" :account="account"/>
  </div>
</template>

<script>
import Summary from './Summary'
import Key from './Key'
import Change from './Change'

export default {
  name: 'License',
  data: () => ({
  }),
  props: {
    loading: Boolean,
    account: Object
  },
  components: { Summary, Key, Change },
}
</script>
