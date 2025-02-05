<template>
   <div class="container">

      <!-- Header Image -->
      <div class="row">
         <div class="col-md-12">
            <img 
               src="../../public/images/jugadores-banner.png" 
               alt="Jugadores Header" 
               class="img-fluid mb-3" 
               style="max-width: 100%; height: auto;"
            />
         </div>
      </div>

      <!-- Alert Message -->
      <div class="row" v-if="!players.length" >
         <div class="col-md-12">
            <div class="alert alert-info text-center" role="alert">
               Cargando jugadores...
            </div>
         </div>
      </div>

      <div class="row align-items-center mb-3">
         <!-- Add Player Button -->
         <div class="col-md-6">
            <button 
               type="button" 
               class="btn btn-secondary" 
               @click="addPlayer">
               Añadir Jugador
            </button>
         </div>
         <!-- Search by Last Name -->
         <div class="col-md-6">
            <div class="input-group">
               <label for="searchInput" class="input-group-text">
                  Buscar:
               </label>
               <input 
                  type="text" 
                  class="form-control" 
                  v-model="lastNameToSearch" 
                  @input="searchPlayersByLastName" 
                  placeholder="Buscar por apellido" >
            </div>
         </div>
      </div>

      <!-- PlayersList Component -->
      <div class="row">
         <div class="col-md-12 mb-3">
            <PlayersList 
               :players="players"
               @view-player="viewPlayer"
               @edit-player="editPlayer"
               @delete-player="deleteOnePlayer"
            /> 
         </div>
      </div>

      <!-- Players pages navigation -->
      <div class="row">
         <div class="col-md-12">
            <button 
               type="text" 
               class="btn btn-secondary btn-sm" 
               @click="goToPage(page - 1)" :disabled="page <= 1">
            Anterior
            </button>
            Página {{ page }} de {{ totalPages }}
            <button 
               type="text" 
               class="btn btn-secondary btn-sm" 
               @click="goToPage(page + 1)" 
               :disabled="page >= totalPages">
            Siguiente
            </button>
         </div>
      </div>

   </div>
</template>

<script>
import PlayersList from '@/components/PlayersList.vue'
import { getAllPlayers, deletePlayer } from '@/api/connectionService'

export default {
   name: 'PlayersView',
   components: { PlayersList },
   data() {
      return {
         players: [],
         totalPlayers: 0,
         page: 1,
         perPage: 10,
         totalPages: 0,
         lastNameToSearch: '',
      }
   },

   methods: {
      async loadPlayers() {
         // Retrieve all players or filtered players with pagination
         try {
            const data = await getAllPlayers(
               this.page, 
               this.perPage,
               this.lastNameToSearch
            )
            
            if (data.status == 'error') {
               console.error(`Backend response error: ${data.message}`)
            } else {
               this.players = data.players
               this.totalPlayers = data.total_players
               this.totalPages = data.pages
               console.log(`${this.totalPlayers} players have been retrieved. Page ${this.page} of ${this.totalPages} is shown.`)
            }

         } catch(err) {
            console.error(`Error retrieving players: ${err}`)
         }
      },

      searchPlayersByLastName() {
         this.page = 1
         this.loadPlayers()
      },

      async goToPage(page) {
         // Players pages navigation
         if (page >= 1 && page <= this.totalPages) {
            this.page = page
            await this.loadPlayers()
         }
      },

      addPlayer() {
         console.log('New player is going to be added')
         this.$router.push({ name: 'AddPlayer'})
      },

      viewPlayer(id) {
         console.log(`PlayersView sends id ${id} to PlayerView` )
         this.$router.push({ name: 'Player', params: { id } })
      },

      editPlayer(id) {
         console.log(`PlayersView sends id ${id} to EditPlayerView` )
         this.$router.push({ name: 'EditPlayer', params: { id } })
      },

      async deleteOnePlayer(id) {
         try {
            await deletePlayer(id)
            this.players = this.players.filter(
               player => player.id != id
            )
            console.log(`Player ${id} has been removed`)
            await this.loadPlayers()

         } catch (err) {
            console.error(`Delete Error: ${err}`)
         }
      }
   },

   async created() {
      await this.loadPlayers()
   }

}
</script>

<style></style>