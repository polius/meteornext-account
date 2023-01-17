<template>
  <div>
    <div class="text-h6 font-weight-medium left" style="letter-spacing:1px!important; text-align:center; cursor:default">PROFILE</div>
    <v-divider style="margin-top:15px; margin-bottom:20px"></v-divider>
    <Summary :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Password :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <MFA :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Delete :account="account"/>
  </div>
</template>

<style scoped>
@media (max-width: 1040px) {
  .left {
    text-align:left !important;
  }
}
</style>

<script>
import Summary from './Summary'
import Password from './Password'
import MFA from './MFA'
import Delete from './Delete'

export default {
  data: () => ({
  }),
  components: { Summary, Password, MFA, Delete },
  props: {
    account: Object
  },
}
</script>
