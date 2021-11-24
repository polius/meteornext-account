<template>
  <div>
    <Summary :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Key :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <div class="text-h6 font-weight-medium">Change license</div>
    <div class="body-1 font-weight-light" style="margin-top:15px">Choose the license that best suits your needs.</div>
    <v-btn color="info" @click="$router.push('/license/change')" style="font-size:0.95rem; font-weight:400; text-transform:none; color:white; margin-top:15px;">Change license</v-btn>
  </div>
</template>

<script>
import Summary from './Summary'
import Key from './Key'

export default {
  name: 'License',
  data: () => ({
  }),
  props: {
    account: Object
  },
  components: { Summary, Key },
}
</script>
