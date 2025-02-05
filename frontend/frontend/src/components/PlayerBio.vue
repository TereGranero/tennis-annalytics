<template>
      <div class="row d-flex flex-wrap gap-3 justify-content-center">
         <!-- Player photo -->
         <div class="col-md-4 d-flex justify-content-center align-items-center">
            <img 
               v-if="urlPlayerImage" 
               :src="urlPlayerImage" 
               :alt="urlPlayerImage" 
               width="200" />
            <span v-else class="text-center"> Imagen no disponible</span>
         </div>  
         <!-- Personal details -->
         <div class="col-md-7">
            <h3 class="mb-3">DETALLES PERSONALES</h3>
            <table class="table table-hover">
               <tbody>
                  <tr v-if="player.country !== 'unknown'">
                     <th scope="row">País</th>
                     <td>

                        <span> {{ countryName }}</span>
                     </td>
                  </tr>
                  <tr>
                     <th scope="row">Nacimiento</th>
                     <td>{{ player.birth_date }}</td>
                  </tr>
                  <tr>
                     <th scope="row">Mano</th>
                     <td>{{ player.hand }}</td>
                  </tr>
                  <tr>
                     <th scope="row">Altura</th>
                     <td>{{ player.height }}</td>
                  </tr>
                  <tr>
                     <th scope="row">Peso</th>
                     <td> ? </td>
                  </tr>
                  <tr>
                     <th scope="row">Profesional desde</th>
                     <td> ? </td>
                  </tr>
               </tbody>
            </table>
         </div>
      </div>
</template>

<script>
import countries from 'i18n-iso-countries'
import es from 'i18n-iso-countries/langs/es.json'
import { getWikiPlayerImage } from '@/api/connectionService'

export default {
   props: {
      player: Object,
   },

   data() {
      return {
         urlPlayerImage: null,
         countryName: null,
      }
   },
   
   watch: {
      'player.wikidata_id': {
         immediate: true, // If value is not null, launches
         handler(newWikidata_id) {
            if (newWikidata_id && newWikidata_id !== '-') {
               this.getPlayerImage();
            }
         }
      },

      'player.country': {
         immediate: true, 
         handler(newCountry) {
            if (newCountry && newCountry !== '-' && newCountry !== 'unknown') {
               this.initCountry();
            }
         }
      }
   },

   methods: {
      initCountry() {
         try {
            countries.registerLocale(es)
            this.countryName = countries.getName(this.player.country.toUpperCase(), 'es')      
         } catch (err) {
            console.error(`Error retrieving country name from i18n-iso-countries: ${err}`)
         }
      },
      
      async getPlayerImage() {
         try{
            this.urlPlayerImage = await getWikiPlayerImage(this.player.wikidata_id)
         } catch (err) {
            console.error(`Error retrieving Wikidata player image: ${err}`)
         }
      },  
   },

   async mounted() {
      this.initCountry()
   },

}
</script>

<style scoped>
   img {
      border: 1px solid #140202;
   }
</style>