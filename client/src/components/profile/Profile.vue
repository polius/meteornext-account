<template>
  <div>
    <div class="text-h6 font-weight-medium left" style="letter-spacing:1px!important; text-align:center">PROFILE</div>
    <v-divider style="margin-top:15px; margin-bottom:20px"></v-divider>
    <Name :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
    <Email :account="account"/>
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
import Name from './Name'
import Email from './Email'
import Password from './Password'
import MFA from './MFA'
import Delete from './Delete'

export default {
  data: () => ({
  }),
  components: { Name, Email, Password, MFA, Delete },
  props: {
    account: Object
  },
}
</script>
