<template>
   <div>
     <PlayerForm @add-player="addPlayer"/>
   </div>
 </template>
 
 <script>
 import PlayerForm from '@/components/PlayerForm.vue';
 import {createPlayer} from '@/api/connectionService'

 export default {
   components: { PlayerForm },

   methods: {
      async addPlayer(player){
         try{
            await createPlayer(player)
            console.log(`Player id: ${player.player_id} has been added successfully`)
            this.$router.push('/players')
            
         }catch(err){
            console.error(`Adding Player Error: ${err}`)
            alert('Error: El jugador no se ha añadido.')
         }
      }
   }
 }
 </script>

<style></style>