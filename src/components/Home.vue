<template>
  <v-container :style="$vuetify.breakpoint.mdAndDown ? '' : 'max-width:98%; padding-top:15px'">
    <div v-show="!$vuetify.breakpoint.mdAndDown">
      <v-row no-gutters>
        <v-col cols="5">
          <Profile style="height:296px"/>
        </v-col>
        <v-col cols="7" style="padding-left:15px">
          <License/>
        </v-col>
      </v-row>
      <Billing style="margin-top:15px"/>
    </div>
    <div v-show="$vuetify.breakpoint.mdAndDown">
      <Profile/>
      <License style="margin-top:15px"/>
      <Billing style="margin-top:15px"/>
    </div>
  </v-container>
</template>

<script>
import Profile from './home/Profile'
import License from './home/License'
import Billing from './home/Billing'

export default {
  name: 'Home',
  data: () => ({
  }),
  components: { Profile, License, Billing },
}
</script>