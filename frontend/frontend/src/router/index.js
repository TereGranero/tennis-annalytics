import { createRouter, createWebHistory } from 'vue-router'
import PlayersView from '@/views/PlayersView.vue'
import AddPlayerView from '@/views/AddPlayerView.vue'
import EditPlayerView from '@/views/EditPlayerView.vue'
import PlayerView from '@/views/PlayerView.vue'

const routes = [
  {
    path: "/players",
    name: "Players",
    component: PlayersView,
  },

  // {
  //   path: "/players-search/:last-name",
  //   name: "SearchPlayers",
  //   component: SearchPlayersView,
  //   props: true,
  // },

  {
    path: "/add-player",
    name: "AddPlayer",
    component: AddPlayerView,
  },

  {
    path: "/edit-player/:id",
    name: "EditPlayer",
    component: EditPlayerView,
    props: true,
  },

  {
    path: "/player/:id",
    name: "Player",
    component: PlayerView,
    props: true,
  },

];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router
