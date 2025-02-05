<template>
   <div class="container">
      <br>
      <!-- Header fullname and flag -->
      <div class="row bg-dark text-white mb-5">
         <div class="d-flex align-items-center justify-content-center text-center w-100">
            <img
               v-if="player.country !== 'unknown'"
               :src="'https://flagcdn.com/w40/' + player.country + '.png'"
               :alt="player.country"
               :title="player.country"
               class="flag me-3"> 
            <h2 class="text-center m-0">
               {{ (player.name_first + ' ' + player.name_last).toUpperCase() }}
            </h2>
         </div>
      </div>

      <!-- Basic information -->
      <PlayerBio :player="player" />

   </div>
</template>

<script>
import PlayerBio from '@/components/PlayerBio.vue'
import { getPlayerById } from '@/api/connectionService'

export default {
   name: 'PlayerView',

   props: {
      id: String,
      required: true
   },

   components: { PlayerBio },

   data() {
      return {
         player: {
            player_id: '',
            name_first: '',
            name_last: '',
            hand: '-',
            birth_date: null,
            country: '-',
            height: '-',
            wikidata_id: '-',
            fullname: '',
         },
      }
   },

   methods: {
      async getPlayer() {
         try {
            const data = await getPlayerById(this.id)
      
            if (data.status == 'error') {
               console.error(`Backend response error: ${data.message}`)
      
            } else {
               this.player = { ...data.player }
               console.log(`Player retrieved: ${JSON.stringify(this.player, null, 2)}`)
            }
         } catch (err) {
            console.error(`Error retrieving player id ${this.id}: ${err}`)
         }
      },
   },

   async mounted() {
      await this.getPlayer()
   },

}
</script>

<style scoped> 
   .flag {
      width: 30px;
      height: 1.5em; 
      vertical-align: middle;
      border: 1px solid #140202;
   }
   h2 {
      height: 1.5em; 
   }
</style>