<template>
  <v-container style="max-width:100%">
    <div v-show="!$vuetify.breakpoint.smAndDown">
      <v-row no-gutters>
        <v-col cols="6" style="padding-right:6px">
          <Profile style="height:296px"/>
        </v-col>
        <v-col cols="6" style="padding-left:6px">
          <License/>
        </v-col>
      </v-row>
      <Billing style="margin-top:12px"/>
    </div>
    <div v-show="$vuetify.breakpoint.smAndDown">
      <Profile/>
      <License style="margin-top:12px"/>
      <Billing style="margin-top:12px"/>
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