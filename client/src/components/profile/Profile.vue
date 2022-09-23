<template>
  <div>
    <Summary :account="account"/>
    <v-divider style="margin-top:20px; margin-bottom:20px"></v-divider>
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

<script>
import Summary from './Summary'
import Name from './Name'
import Email from './Email'
import Password from './Password'
import MFA from './MFA'
import Delete from './Delete'

export default {
  data: () => ({
  }),
  components: { Summary, Name, Email, Password, MFA, Delete },
  props: {
    account: Object
  },
}
</script>
