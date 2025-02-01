<template>
   <div>
      <!-- Conditional title -->
      <h2>{{ editing ? 'Modificar Jugador' : 'Añadir Jugador' }}</h2>

      <form @submit.prevent="sendForm">
         <div class="container">

            <!-- Last Name -->
            <div class="row justify-content-center">
               <div class="col-md-6">
                  <div class="form-group">
                     <label>Apellido: </label>
                     <input 
                        ref="reference"
                        type="text" 
                        class="form-control"
                        :class="{'is-invalid': processing && invalidLastName}"
                        @focus="resetState"
                        @keypress="resetState"
                        v-model="player.name_last">
                     <div v-if="processing && invalidLastName" class="invalid-feedback">
                        Debes rellenar el campo Apellido
                     </div>
                  </div>
               </div>
            </div>
         
            <!-- First Name -->
            <div class="row justify-content-center">
               <div class="col-md-6">
                  <div class="form-group">
                     <label>Nombre: </label>
                     <input 
                        type="text" 
                        class="form-control"
                        :class="{'is-invalid': processing && invalidFirstName}"
                        @focus="resetState"
                        v-model="firstName">
                     <div v-if="processing && invalidFirstName" class="invalid-feedback">
                        Debes rellenar el campo Nombre
                     </div>
                  </div>
               </div>
            </div>

            <!-- Birth Date -->
            <div class="row justify-content-center">
               <div class="col-md-6">
                  <div class="form-group">
                     <label>Fecha de nacimiento:</label>
                     <input 
                        type="date" 
                        class="form-control"
                        :class="{'is-invalid': processing && invalidBirthDate}"
                        @focus="resetState"
                        v-model="player.birth_date">
                     <div v-if="processing && invalidBirthDate" class="invalid-feedback">
                        Debes seleccionar una fecha válida
                     </div>
                  </div>
               </div>
            </div>

            <!-- Country -->
            <div class="row justify-content-center">
               <div class="col-md-6">
                  <div class="form-group">
                     <label>País:</label>
                     <select
                        class="form-control"
                        :class="{'is-invalid': processing && invalidCountry}"
                        @focus="resetState"
                        v-model="player.country">
                        <option 
                           v-for="country in allCountries"
                           :key="country.code"
                           :value="country.code">
                           {{ country.name }}
                        </option>
                     </select>
                     <div v-if="processing && invalidCountry" class="invalid-feedback">
                        Debes seleccionar un país
                     </div>
                  </div>
               </div>
            </div>
         
            <!-- Height -->
            <div class="row justify-content-center">
               <div class="col-md-6">
                  <div class="form-group">
                     <label>Altura (cm): </label>
                     <input 
                        type="text" 
                        class="form-control"
                        :class="{'is-invalid': processing && invalidHeight}"
                        @focus="resetState"
                        v-model="player.height">
                     <div v-if="processing && invalidHeight" class="invalid-feedback">
                        Debes proporcionar una altura en centímetros
                     </div>
                  </div>
               </div>
            </div>

            <!-- Hand -->
            <div class="row justify-content-center">
               <div class="col-md-6">
                  <div class="form-group">
                     <label>Mano:</label>
                     <select
                        class="form-control"
                        :class="{'is-invalid': processing && invalidHand}"
                        @focus="resetState"
                        v-model="player.hand">
                        <option 
                           v-for="hand in allHands"
                           :key="hand"
                           :value="hand">
                           {{ hand }}
                        </option>
                     </select>
                     <div v-if="processing && invalidHand" class="invalid-feedback">
                        Debes seleccionar la mano con la que juega 
                     </div>
                  </div>
               </div>
            </div>

            <!-- Wikidata ID -->
            <div class="row justify-content-center">
               <div class="col-md-6">
                  <div class="form-group">
                     <label>Wikidata Id: </label>
                     <input 
                        type="text" 
                        class="form-control"
                        @focus="resetState"
                        v-model="player.wikidata_id">
                  </div>
               </div>
            </div>

            <!-- Buttons -->
            <div class="row">
               <div class="col-md-12">
                  <div class="form-group">
                  <button type="submit" class="btn btn-secondary">Aceptar</button>
                  <button type="button" class="btn btn-outline-secondary ml-2" @click="cancelForm">Cancelar</button>
                  </div>
               </div>
            </div>

         </div>
      </form>
   </div>
</template>

<script>
import countries from 'i18n-iso-countries'
import es from 'i18n-iso-countries/langs/es.json'
import { getPlayerById } from '@/api/connectionService'

export default {
   props: {
      id: {
         type: String,
         default: null,
      }
   },

   data() {
      return {
         player: {
            "player_id": '',
            "name_last": '',
            "hand": '-',
            "birth_date": null,
            "country": '-',
            "height": '-',
            "wikidata_id": '-',
            "fullname": '',
         },
         firstName: '', //not in DB
         allCountries: [],  //comes from library
         allHands: ['-', 'Derecha', 'Izquierda'],
         processing: false,
         error: false,
      }
   },

   computed: {
      editing() {
         console.log(`Checking if there is an id for editing: ${this.id}`)
         return this.id !== null
      },

      formattedFirstName() {
         // Checks if fistName is already formatted as initials
         const isFormatted = this.firstName
            .split(' ')
            .every(word => /^[A-Z](\.[A-Z])*\.$/.test(word))

         if (isFormatted) {
            return this.firstName
         }
         // Formats as initials
         return this.firstName
            .split(' ')
            .map((word) => word.charAt(0).toUpperCase() + '.')
            .join('');
      },

      // --------------------------- Validates Form ---------------------------
      
      invalidLastName() {
         return this.player.name_last < 1
      },

      invalidFirstName() {
         return this.firstName < 1
      },

      invalidBirthDate() {
         return ( 
            !this.player.birth_date || 
            new Date(this.player.birth_date) >= new Date()
         ) 
      },
      
      invalidCountry() {
         return (
            !this.player.country || 
            this.player.country == '-'
         )
      },

      invalidHeight() {
         return (
            this.player.height && 
            this.player.height !== '-' && 
            (parseInt(this.player.height, 10) < 100 || 
               parseInt(this.player.height, 10) > 270)
         )

      },
            
      invalidHand() {
         return ( 
            !this.player.hand || 
            this.player.hand == '-'
         )
      },
   },

   watch: {
      // Launches method updateFullname when name_last or firstName is updated
      'player.name_last': 'updateFullname',
      firstName : 'updateFullname',
   },

   methods: {
      initCountries() {
         countries.registerLocale(es)
         // countries.getNames('es') -> object code:name
         // Object.entries -> array of [code, name]
         // .map(([code, name]) --> array de objetos { code: "ES", name: "España" }
         this.allCountries = Object.entries(countries.getNames('es')).map(([code, name]) => ({
            code,
            name,
         })).sort((a, b) => a.name.localeCompare(b.name))
      },

      generatePlayerId() {
         return 'A' + (Math.floor(Math.random()*10000000)).toString()
      },

      updateFullname() {
         this.player.fullname = `${this.player.name_last} ${this.formattedFirstName}`
      },

      sendForm() {
         this.processing = true
         this.resetState()

         // Validates fields
         if(this.invalidLastName || this.invalidFirstName || this.invalidBirthDate || this.invalidCountry || this.invalidHeight || this.invalidHand) {
            this.error = true
            return
         }

         // Sends events
         if (this.editing) {
            console.log(`Player updated to: ${JSON.stringify(this.player, null, 2)}`) // 2spaces identation   REVISA SI ES this.player O QUE...
            this.$emit('edit-player', this.player.player_id, this.player)

         } else {
            // Assigns new player_id
            this.player.player_id = this.generatePlayerId()

            console.log(`New player is: ${JSON.stringify(this.player, null, 2)}`)
            this.$emit('add-player', this.player)
         }

         // Resets form and variables
         this.player = {
            "player_id": '',
            "name_last": '',
            "hand": '-',
            "birth_date": null,
            "country": '-',
            "height": '-',
            "wikidata_id": '-',
            "fullname": '',
         },
         this.firstName = ''
         this.processing = false
         this.error = false
      },
      
      resetState(){
         this.error = false
      },

      cancelForm(){
         this.$router.push('/players')
      },
   },

   async mounted() {
      if (this.editing) {
         
         console.log(`Editing player id: ${this.id}`)
         const data = await getPlayerById(this.id)

         if (data.status == 'error') {
            console.error(`Backend response error: ${data.message}`)

         } else {
            this.player = { ...data.player }
            console.log(`Player retrieved: ${JSON.stringify(this.player, null, 2)}`)

            // Extracts first name
            this.firstName = this.player.fullname.replace(this.player.name_last, '').trim()

            // Capitalizes country
            if (this.player.country) {
               this.player.country = this.player.country.toUpperCase()
            }

            // Formats birth date dd-mm-yyyy --> yyyy-mm-dd
            if (this.player.birth_date) {
               const [day, month, year] = this.player.birth_date.split("-")
               this.player.birth_date = `${year}-${month}-${day}`
            }
         }
      }
      this.initCountries()
   }
}
</script>

<style scoped>
   form {
      margin-bottom: 2rem;
   }
</style>