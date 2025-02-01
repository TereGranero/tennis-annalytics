<template>
   <table class="table table-hover">
      <thead>
         <tr>
            <th scope="col">Nombre</th>
            <th scope="col">País</th>
            <th scope="col">Nacimiento</th>
            <th scope="col"></th>
         </tr>
      </thead>
      <tbody>
         <PlayerItem 
            v-for="player in players" 
            :key="player.id"
            :player="player"
            @view-player="viewPlayer"
            @edit-player="editPlayer"
            @delete-player="deleteOnePlayer" 
         /> 
      </tbody>
   </table>
</template>

<script>
import PlayerItem from './PlayerItem.vue'

export default {
   components: { PlayerItem },

   props: {
      players: Array,
   },
   
   methods:{
      viewPlayer(id){
         this.$emit('view-player',id)
      },

      editPlayer(id){
         this.$emit('edit-player',id)
      },

      deleteOnePlayer(id){
         this.$emit('delete-player', id)
      },
   },

}
</script>

<style></style>